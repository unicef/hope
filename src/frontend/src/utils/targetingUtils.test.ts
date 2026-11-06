import { describe, expect, it } from 'vitest';
import type { FspChoices } from '@restgenerated/models/FspChoices';
import { deliveryMechanismChoicesForFsp } from './targetingUtils';

const fspChoices = [
  {
    deliveryMechanism: { code: 'cash', name: 'Cash', accountType: null },
    fsps: [{ id: 'fsp-a', name: 'FSP A' }],
  },
  {
    deliveryMechanism: {
      code: 'mobile_money',
      name: 'Mobile Money',
      accountType: 2,
    },
    fsps: [
      { id: 'fsp-a', name: 'FSP A' },
      { id: 'fsp-b', name: 'FSP B' },
    ],
  },
  {
    deliveryMechanism: { code: 'transfer', name: 'Transfer', accountType: 3 },
    fsps: [{ id: 'fsp-b', name: 'FSP B' }],
  },
] as unknown as FspChoices[];

describe('deliveryMechanismChoicesForFsp', () => {
  it('keeps only the delivery mechanisms the FSP supports', () => {
    expect(deliveryMechanismChoicesForFsp(fspChoices, 'fsp-a')).toEqual([
      { name: 'Cash', value: 'cash', accountType: null },
      { name: 'Mobile Money', value: 'mobile_money', accountType: 2 },
    ]);
  });

  it('returns nothing when there is no FSP', () => {
    expect(deliveryMechanismChoicesForFsp(fspChoices, null)).toEqual([]);
    expect(deliveryMechanismChoicesForFsp(fspChoices, undefined)).toEqual([]);
  });

  it('returns nothing for an FSP not allowed in the business area', () => {
    expect(deliveryMechanismChoicesForFsp(fspChoices, 'fsp-x')).toEqual([]);
  });
});
