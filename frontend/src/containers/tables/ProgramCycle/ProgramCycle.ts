export default interface ProgramCycle {
  id: string;
  unicef_id: string;
  title: string;
  status: string;
  total_entitled_quantity?: number;
  total_undelivered_quantity?: number;
  total_delivered_quantity?: number;
  start_date: string;
  end_date?: string;
}
