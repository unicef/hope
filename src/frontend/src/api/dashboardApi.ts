import { api } from '@api/api';

export interface HouseholdPayment {
  id: string;
  delivered_quantity: number;
  delivery_date: Date;
  delivered_quantity_usd: number;
  currency: string;
  fsp: string;
  status: string;
  delivery_type: string;
  payment_status: string;
  program: string;
  sector: string;
  children_count: number;
  size: number;
}

export interface Household {
  id: string;
  business_area: string;
  program: string;
  size: number;
  first_registration_date: string;
  admin1: string | null;
  admin2: string | null;
  sector: string;
  children_count: number;
  payments: HouseholdPayment[];
}

export const fetchDashboardData = async (
  businessArea: string,
): Promise<Household[]> => {
  return api.get(`dashboard/${businessArea}/`);
};
