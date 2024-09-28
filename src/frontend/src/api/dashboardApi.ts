import { api } from '@api/api';

export interface HouseholdPayment {
  delivered_quantity: string;
  delivery_date: string;
  delivered_quantity_usd: string;
  currency: string;
  fsp: string;
  delivery_type: string;
  status: string;
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
