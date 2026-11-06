import { PlanTypeEnum } from '@restgenerated/models/PlanTypeEnum';
import { describe, expect, it } from 'vitest';
import { paymentListTitleLabel } from './utils';

describe('paymentListTitleLabel', () => {
  it.each([
    [PlanTypeEnum.REGULAR, 'Payment List'],
    [undefined, 'Payment List'],
    [PlanTypeEnum.FOLLOW_UP, 'Follow-up Payment List'],
    [PlanTypeEnum.TOP_UP, 'Top Up Payment List'],
    [PlanTypeEnum.TOP_UP_AMENDMENT, 'Top Up Amendment Payment List'],
  ])('titles a %s list "%s"', (planType, title) => {
    expect(paymentListTitleLabel(planType)).toBe(title);
  });
});
