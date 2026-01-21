export interface KpiResult {
    date: string; // YYYY-MM
    value: number;
}

export interface KpiRow {
    name: string;
    data: number[]; // Array of values matching the months
    total: number;
    isRatio?: boolean;
}

export interface DashboardData {
    months: string[]; // ['2024-01', '2024-02', ...]

    // Tables
    commerce: KpiRow[];
    analyse: KpiRow[];
    signed: KpiRow[]; // Mixed
    ratios: KpiRow[];
    analyseSigned: KpiRow[];

    // Charts Data (Simplified for Plotly)
    charts: {
        commerceInput: any[];
        commerceSigned: any[];
        analyseInput: any[];
        analyseSigned: any[];
        catCommerce: any[];
        catCommerceSigned: any[];
        catAnalyse: any[];
        catAnalyseSigned: any[];
    };

    // Raw category data for Export
    categories: {
        commerce: any[];
        commerceSigned: any[];
        analyse: any[];
        analyseSigned: any[];
    };
}
