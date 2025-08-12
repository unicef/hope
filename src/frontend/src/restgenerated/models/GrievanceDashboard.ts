/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChartData } from './ChartData';
import type { DetailedChartData } from './DetailedChartData';
import type { TicketsByType } from './TicketsByType';
export type GrievanceDashboard = {
    ticketsByType: TicketsByType;
    ticketsByStatus: ChartData;
    ticketsByCategory: ChartData;
    ticketsByLocationAndCategory: DetailedChartData;
};

