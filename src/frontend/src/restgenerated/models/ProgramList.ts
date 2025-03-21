/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BeneficiaryGroup } from './BeneficiaryGroup';
import type { DataCollectingType } from './DataCollectingType';
import type { FrequencyOfPaymentsEnum } from './FrequencyOfPaymentsEnum';
import type { SectorEnum } from './SectorEnum';
import type { Status791Enum } from './Status791Enum';
export type ProgramList = {
  id: string;
  /**
   * Program code
   */
  programme_code?: string | null;
  /**
   * Program slug [sys]
   */
  slug: string;
  /**
   * Program name
   */
  name: string;
  /**
   * Program start date
   */
  start_date: string;
  /**
   * Program end date
   */
  end_date?: string | null;
  /**
   * Program budget
   */
  budget: string;
  /**
   * Program frequency of payments
   *
   * * `ONE_OFF` - One-off
   * * `REGULAR` - Regular
   */
  frequency_of_payments: FrequencyOfPaymentsEnum;
  /**
   * Program sector
   *
   * * `CHILD_PROTECTION` - Child Protection
   * * `EDUCATION` - Education
   * * `HEALTH` - Health
   * * `MULTI_PURPOSE` - Multi Purpose
   * * `NUTRITION` - Nutrition
   * * `SOCIAL_POLICY` - Social Policy
   * * `WASH` - WASH
   */
  sector: SectorEnum;
  /**
   * Program cash+
   */
  cash_plus: boolean;
  /**
   * Program population goal
   */
  population_goal: number;
  data_collecting_type: DataCollectingType;
  beneficiary_group: BeneficiaryGroup;
  /**
   * Status
   *
   * * `ACTIVE` - Active
   * * `DRAFT` - Draft
   * * `FINISHED` - Finished
   */
  status: Status791Enum;
  readonly pdu_fields: Array<string>;
  /**
   * Program household count [sys]
   */
  household_count?: number;
};
