import { Injectable } from '@angular/core';
import * as XLSX from 'xlsx';
import { DashboardData, KpiRow } from '../models/data.model';

@Injectable({
    providedIn: 'root'
})
export class KpiService {

    // Configuration Constants
    private readonly ASSOCIATES_SMART = ["AC", "FP", "PB", "DDL", "CA"];
    private readonly ASSOCIATES_SMARTPLUS = ["LP", "DP", "GP", "GB", "PM"];
    private readonly TARGET_CATEGORIES = [
        "Télécoms", "Energie", "Transports", "Copieurs",
        "Facilities", "Déchets", "QOFI / Location Engins / EPI", "Matériel IT"
    ];

    constructor() { }

    /**
     * Reads an Excel file and returns the raw data as JSON.
     */
    async loadData(file: File): Promise<any[]> {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e: any) => {
                try {
                    const bstr = e.target.result;
                    const wb = XLSX.read(bstr, { type: 'binary', cellDates: true });
                    const wsname = wb.SheetNames[0]; // Assume first sheet
                    const ws = wb.Sheets[wsname];
                    // Header on index 1 (row 2 in Excel) -> range: 1
                    const data = XLSX.utils.sheet_to_json(ws, { range: 1 });
                    resolve(data);
                } catch (err) {
                    reject(err);
                }
            };
            reader.onerror = (err) => reject(err);
            reader.readAsBinaryString(file);
        });
    }

    /**
     * Main calculation function.
     */
    calculateDashboard(rawData: any[]): DashboardData {
        const months = this.generateLast24Months();
        const data = this.preprocessData(rawData);

        // --- 1. Commerce ---
        const commTotal = this.countProjects(data, months, 'Commerce');
        const commG1 = this.countProjects(data, months, 'Commerce', this.ASSOCIATES_SMART);
        const commG2 = this.countProjects(data, months, 'Commerce', this.ASSOCIATES_SMARTPLUS);

        // Fix: Cast to any to add properties not on the internal type
        const commDiv15: any = this.divideRow(commTotal, 15);
        commDiv15.isRatio = true;
        commDiv15.name = 'Commerce / 15';

        const commerceRows: KpiRow[] = [
            { name: 'Commerce Total', ...commTotal },
            { name: 'Smart', ...commG1 },
            { name: 'Smart +', ...commG2 },
            commDiv15 as KpiRow
        ];

        // --- 2. Analyse ---
        const analTotal = this.countProjects(data, months, 'Analyse');
        const analG1 = this.countProjects(data, months, 'Analyse', this.ASSOCIATES_SMART);
        const analG2 = this.countProjects(data, months, 'Analyse', this.ASSOCIATES_SMARTPLUS);

        const analyseRows: KpiRow[] = [
            { name: 'Analyse Total', ...analTotal },
            { name: 'Smart', ...analG1 },
            { name: 'Smart +', ...analG2 }
        ];

        // --- 3. Signatures (Commerce) ---
        const signTotal = this.countProjects(data, months, 'Commerce', undefined, undefined, true);
        const signG1 = this.countProjects(data, months, 'Commerce', this.ASSOCIATES_SMART, undefined, true);
        const signG2 = this.countProjects(data, months, 'Commerce', this.ASSOCIATES_SMARTPLUS, undefined, true);

        const signedRows: KpiRow[] = [
            { name: 'Commerce Signe Total', ...signTotal },
            { name: 'Smart', ...signG1 },
            { name: 'Smart +', ...signG2 }
        ];

        // Ratios
        const ratioTotal = this.calculateRatio(signTotal, commTotal, 'Taux de contrats signés');
        const ratioG1 = this.calculateRatio(signG1, commG1, 'Taux de contrats signés Smart');
        const ratioG2 = this.calculateRatio(signG2, commG2, 'Taux de contrats signés Smart +');

        const ratioRows: KpiRow[] = [ratioTotal, ratioG1, ratioG2];

        // --- 4. Analyse Signe ---
        const analSignTotal = this.countProjects(data, months, 'Analyse', undefined, undefined, true);
        const analSignG1 = this.countProjects(data, months, 'Analyse', this.ASSOCIATES_SMART, undefined, true);
        const analSignG2 = this.countProjects(data, months, 'Analyse', this.ASSOCIATES_SMARTPLUS, undefined, true);

        const analyseSignedRows: KpiRow[] = [
            { name: 'Analyse Signe Total', ...analSignTotal },
            { name: 'Smart', ...analSignG1 },
            { name: 'Smart +', ...analSignG2 }
        ];

        // --- 5. Categories ---
        // Helper to get category rows
        const getCatData = (suffix: string, type: string, isSigned: boolean) =>
            this.TARGET_CATEGORIES.map(cat => ({
                cat,
                ...this.countProjects(data, months, type, undefined, [cat], isSigned)
            }));

        const catComm = getCatData('Commerce', 'Commerce', false);
        const catCommSign = getCatData('Commerce Signe', 'Commerce', true);
        const catAnal = getCatData('Analyse', 'Analyse', false);
        const catAnalSign = getCatData('Analyse Signe', 'Analyse', true);

        return {
            months,
            commerce: commerceRows,
            analyse: analyseRows,
            signed: signedRows,
            ratios: ratioRows,
            analyseSigned: analyseSignedRows,
            charts: {
                commerceInput: this.toPlotly(commerceRows.slice(1, 3), months), // G1, G2
                commerceSigned: this.toPlotly(signedRows.slice(1, 3), months),
                analyseInput: this.toPlotly(analyseRows.slice(1, 3), months),
                analyseSigned: this.toPlotly(analyseSignedRows.slice(1, 3), months),
                catCommerce: this.toPlotlyCats(catComm, months, 'Commerce'),
                catCommerceSigned: this.toPlotlyCats(catCommSign, months, 'Commerce Signe'),
                catAnalyse: this.toPlotlyCats(catAnal, months, 'Analyse'),
                catAnalyseSigned: this.toPlotlyCats(catAnalSign, months, 'Analyse Signe'),
            },
            categories: {
                commerce: catComm,
                commerceSigned: catCommSign,
                analyse: catAnal,
                analyseSigned: catAnalSign
            }
        };
    }

    /**
     * Exports the DashboardData to an Excel file.
     * Replicates the exact structure of the legacy "Donnees_Brutes_KPI.xlsx"
     * (Single sheet, specific order with spacers)
     */
    exportExcel(data: DashboardData) {
        const wb = XLSX.utils.book_new();

        // 1. Prepare Header
        const header = ['KPI', ...data.months, 'Total'];
        const body: any[][] = [];

        // Helper to add rows
        const addRows = (rows: KpiRow[]) => {
            rows.forEach(r => {
                body.push([
                    r.name,
                    ...r.data.map(v => r.isRatio ? `${(v * 100).toFixed(0)}%` : v),
                    r.isRatio ? `${(r.total * 100).toFixed(0)}%` : r.total
                ]);
            });
        };

        // Helper to add Category rows
        // Map {cat, data[], total} to the same structure
        const addCatRows = (catGroup: any[], suffix: string) => {
            catGroup.forEach(c => {
                const name = `${c.cat} ${suffix}`.trim(); // Reconstruct name like legacy: "CatName Suffix"
                body.push([
                    name,
                    ...c.data,
                    c.total
                ]);
            });
        };

        // Helper to add Spacer
        const addSpacer = () => {
            body.push(['', ...data.months.map(() => ''), '']);
        };

        // --- Sequence Matching extraction_data.py ---

        // 1. Commerce
        addRows(data.commerce);
        addSpacer();

        // 2. Analyse
        addRows(data.analyse);
        addSpacer();

        // 3. Commerce Signé + Ratios
        // Legacy put Ratios immediately after Signed block, before the spacer
        addRows(data.signed);
        addRows(data.ratios);
        addSpacer();

        // 4. Analyse Signé
        addRows(data.analyseSigned);
        addSpacer();

        // 5. Categories
        // Order: Commerce, Commerce Signé, Analyse, Analyse Signé
        // Each followed by spacer

        // Cat Commerce
        addCatRows(data.categories.commerce, 'Commerce');
        addSpacer();

        // Cat Commerce Signé
        addCatRows(data.categories.commerceSigned, 'Commerce Signe');
        addSpacer();

        // Cat Analyse
        addCatRows(data.categories.analyse, 'Analyse');
        addSpacer();

        // Cat Analyse Signé
        addCatRows(data.categories.analyseSigned, 'Analyse Signe');

        // Create Sheet
        const ws = XLSX.utils.aoa_to_sheet([header, ...body]);
        XLSX.utils.book_append_sheet(wb, ws, 'Donnees_Brutes_KPI');

        // Save
        XLSX.writeFile(wb, 'Donnees_Brutes_KPI.xlsx');
    }

    // --- Internals ---

    private generateLast24Months(): string[] {
        const months: string[] = [];
        const end = new Date();
        // Start 24 months ago
        const start = new Date(end.getFullYear(), end.getMonth() - 23, 1);

        let current = start;
        for (let i = 0; i < 24; i++) {
            const y = current.getFullYear();
            const m = String(current.getMonth() + 1).padStart(2, '0');
            months.push(`${y}-${m}`);
            current = new Date(current.getFullYear(), current.getMonth() + 1, 1);
        }
        return months;
    }

    private preprocessData(data: any[]): any[] {
        // Define robust mapping
        // Internal Key <- Possible Headers (slugified)

        const slugify = (s: string) => s.normalize('NFD').replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();

        // Map Internal Key to Expected Slug
        const keyMap: { [internal: string]: string } = {
            'type_de_projet': 'type de projet',
            'associe': 'associe',
            'categorie': 'categorie',
            'date_entree': 'date d\'entree',
            'date_signature': 'date de signature',
            'etat_1': 'etat 1',
            'etat_2': 'etat 2',
            'etat_3': 'etat 3',
            'etat_4': 'etat 4'
        };

        return data.map(row => {
            const newRow: any = {};

            Object.keys(row).forEach(header => {
                const slug = slugify(header);

                if (slug === keyMap['type_de_projet']) newRow['type_de_projet'] = row[header];
                else if (slug === keyMap['associe']) newRow['associe'] = row[header];
                else if (slug === keyMap['categorie']) newRow['categorie'] = row[header];
                else if (slug.includes('date') && slug.includes('entree')) newRow['date_entree'] = row[header];
                else if (slug.includes('date') && slug.includes('signature')) newRow['date_signature'] = row[header];
                else if (slug === keyMap['etat_1']) newRow['etat_1'] = row[header];
                else if (slug === keyMap['etat_2']) newRow['etat_2'] = row[header];
                else if (slug === keyMap['etat_3']) newRow['etat_3'] = row[header];
                else if (slug === keyMap['etat_4']) newRow['etat_4'] = row[header];
            });

            return newRow;
        });
    }

    private countProjects(
        data: any[],
        months: string[],
        type: string,
        associates?: string[],
        categories?: string[],
        isSigned: boolean = false
    ): { data: number[], total: number } {

        // Helper: safe date parser
        const parseDate = (val: any): Date | null => {
            if (val instanceof Date) return val;
            if (!val) return null;

            // Try standard Date parsing
            const d = new Date(val);
            if (!isNaN(d.getTime())) return d;

            // Try DD/MM/YYYY (French format common in these files)
            if (typeof val === 'string' && val.match(/^\d{1,2}\/\d{1,2}\/\d{4}/)) {
                const parts = val.split('/');
                if (parts.length === 3) {
                    const day = parseInt(parts[0], 10);
                    const month = parseInt(parts[1], 10) - 1;
                    const year = parseInt(parts[2], 10);
                    const dFixed = new Date(year, month, day);
                    if (!isNaN(dFixed.getTime())) return dFixed;
                }
            }
            return null;
        };

        const filtered = data.filter(row => {
            // 1. Project Type
            const rowType = String(row['type_de_projet'] || '').trim().toLowerCase();
            if (rowType !== type.toLowerCase()) return false;

            // 2. Associates (Compare lower to lower)
            if (associates) {
                const rowAssoc = String(row['associe'] || '').trim().toLowerCase();
                const targetAssociates = associates.map(a => a.toLowerCase());
                if (!targetAssociates.includes(rowAssoc)) return false;
            }

            // 3. Categories
            if (categories) {
                const rowCat = String(row['categorie'] || '').trim().toLowerCase();
                if (!categories.some(c => c.toLowerCase() === rowCat)) return false;
            }

            // 4. Signed
            if (isSigned) {
                const states = [row['etat_1'], row['etat_2'], row['etat_3'], row['etat_4']];
                const hasSigned = states.some(st => String(st || '').trim().toLowerCase() === 'signé');
                if (!hasSigned) return false;
            }

            return true;
        });

        // Bucketize by month
        const counts = new Array(months.length).fill(0);
        const dateField = isSigned ? "date_signature" : "date_entree";

        filtered.forEach(row => {
            const dateVal = parseDate(row[dateField]);

            if (dateVal) {
                // Fix for Timezone shifting:
                // Excel dates often come as midnight (00:00:00). 
                // Timezone offsets can shift this to 23:00:00 of the PREVIOUS day.
                // We add 12 hours to be safely in the middle of the day.
                const safeDate = new Date(dateVal);
                safeDate.setHours(safeDate.getHours() + 12);

                const y = safeDate.getFullYear();
                const m = String(safeDate.getMonth() + 1).padStart(2, '0');
                const key = `${y}-${m}`;
                const idx = months.indexOf(key);
                if (idx >= 0) {
                    counts[idx]++;
                }
            }
        });

        const total = counts.reduce((a, b) => a + b, 0);
        return { data: counts, total };
    }

    private divideRow(source: { data: number[], total: number }, divisor: number) {
        return {
            data: source.data.map(v => Number((v / divisor).toFixed(2))),
            total: Number((source.total / divisor).toFixed(2))
        };
    }

    private calculateRatio(
        numerator: { data: number[], total: number },
        denominator: { data: number[], total: number },
        name: string
    ): KpiRow {
        const data = numerator.data.map((num, i) => {
            const den = denominator.data[i];
            return den === 0 ? 0 : Number((num / den).toFixed(2));
        });
        const total = denominator.total === 0 ? 0 : Number((numerator.total / denominator.total).toFixed(2));

        return { name, data, total, isRatio: true };
    }

    // --- Formatting for Plotly ---
    // Using the specific colors from V1
    private readonly C_G1 = '#2C3E50';
    private readonly C_G2 = '#5B80A4';
    private readonly CAT_COLORS = [
        '#E74C3C', '#8E44AD', '#3498DB', '#1ABC9C',
        '#F1C40F', '#E67E22', '#7F8C8D', '#34495E'
    ];

    private toPlotly(rows: KpiRow[], months: string[]) {
        return rows.map(r => {
            let color = this.C_G1;
            if (r.name.includes("Smart +") || r.name.includes("LP DP")) color = this.C_G2;

            return {
                x: months,
                y: r.data,
                type: 'bar',
                name: r.name,
                marker: { color }
            };
        });
    }

    private toPlotlyCats(catData: any[], months: string[], suffix: string) {
        return catData.map((item, i) => ({
            x: months,
            y: item.data,
            type: 'bar',
            name: item.cat, // Clean name
            marker: { color: this.CAT_COLORS[i % this.CAT_COLORS.length] }
        }));
    }

    /**
     * Generates mock data for the demo mode.
     */
    generateDemoData(): DashboardData {
        const months = this.generateLast24Months();

        // Helper to generate random row
        const mockRow = (name: string, min: number, max: number, isRatio = false): KpiRow => {
            const data = months.map(() => {
                if (isRatio) return Number((Math.random() * (max - min) + min).toFixed(2));
                return Math.floor(Math.random() * (max - min + 1)) + min;
            });
            // For ratio, total is average, else sum
            const total = isRatio
                ? Number((data.reduce((a, b) => a + b, 0) / data.length).toFixed(2))
                : data.reduce((a, b) => a + b, 0);
            return { name, data, total, isRatio };
        };

        // 1. Commerce
        const commG1 = mockRow('Smart', 10, 25);
        const commG2 = mockRow('Smart +', 5, 15);

        // Calculate total from parts
        const commTotalData = commG1.data.map((v, i) => v + commG2.data[i]);
        const commTotal: KpiRow = {
            name: 'Commerce Total',
            data: commTotalData,
            total: commTotalData.reduce((a, b) => a + b, 0)
        };

        // Fix cast here too
        const commDiv15: any = this.divideRow(commTotal, 15);
        commDiv15.isRatio = true;
        commDiv15.name = 'Commerce / 15';

        const commerceRows = [commTotal, commG1, commG2, (commDiv15 as KpiRow)];

        // 2. Analyse
        const analG1 = mockRow('Smart', 8, 20);
        const analG2 = mockRow('Smart +', 2, 8);
        const analTotalData = analG1.data.map((v, i) => v + analG2.data[i]);
        const analTotal: KpiRow = {
            name: 'Analyse Total',
            data: analTotalData,
            total: analTotalData.reduce((a, b) => a + b, 0)
        };

        const analyseRows = [analTotal, analG1, analG2];

        // 3. Signed
        const signG1 = mockRow('Smart', 5, 15);
        const signG2 = mockRow('Smart +', 2, 8);
        const signTotalData = signG1.data.map((v, i) => v + signG2.data[i]);
        const signTotal: KpiRow = {
            name: 'Commerce Signe Total',
            data: signTotalData,
            total: signTotalData.reduce((a, b) => a + b, 0)
        };

        const signedRows = [signTotal, signG1, signG2];

        // Ratios
        const ratioTotal = this.calculateRatio(signTotal, commTotal, 'Taux de contrats signés');
        const ratioG1 = this.calculateRatio(signG1, commG1, 'Taux de contrats signés Smart');
        const ratioG2 = this.calculateRatio(signG2, commG2, 'Taux de contrats signés Smart +');
        const ratioRows = [ratioTotal, ratioG1, ratioG2];

        // 4. Analyse Signed
        const analSignG1 = mockRow('Smart', 4, 12);
        const analSignG2 = mockRow('Smart +', 1, 5);
        const analSignTotalData = analSignG1.data.map((v, i) => v + analSignG2.data[i]);
        const analSignTotal: KpiRow = {
            name: 'Analyse Signe Total',
            data: analSignTotalData,
            total: analSignTotalData.reduce((a, b) => a + b, 0)
        };

        const analyseSignedRows = [analSignTotal, analSignG1, analSignG2];

        // 5. Cats
        const getMockCats = (suffix: string) => this.TARGET_CATEGORIES.map(cat => ({
            cat,
            ...mockRow(cat + ' ' + suffix, 0, 8)
        }));

        const catComm = getMockCats('Commerce');
        const catCommSign = getMockCats('Commerce Signe');
        const catAnal = getMockCats('Analyse');
        const catAnalSign = getMockCats('Analyse Signe');

        return {
            months,
            commerce: commerceRows,
            analyse: analyseRows,
            signed: signedRows,
            ratios: ratioRows,
            analyseSigned: analyseSignedRows,
            charts: {
                commerceInput: this.toPlotly(commerceRows.slice(1, 3), months),
                commerceSigned: this.toPlotly(signedRows.slice(1, 3), months),
                analyseInput: this.toPlotly(analyseRows.slice(1, 3), months),
                analyseSigned: this.toPlotly(analyseSignedRows.slice(1, 3), months),
                catCommerce: this.toPlotlyCats(catComm, months, 'Commerce'),
                catCommerceSigned: this.toPlotlyCats(catCommSign, months, 'Commerce Signe'),
                catAnalyse: this.toPlotlyCats(catAnal, months, 'Analyse'),
                catAnalyseSigned: this.toPlotlyCats(catAnalSign, months, 'Analyse Signe'),
            },
            categories: {
                commerce: catComm,
                commerceSigned: catCommSign,
                analyse: catAnal,
                analyseSigned: catAnalSign
            }
        };
    }
}
