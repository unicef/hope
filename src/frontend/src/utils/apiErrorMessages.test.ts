import { describe, expect, it, vi } from 'vitest';
import { getApiErrorMessages, showApiErrorMessages } from './utils';

describe('API error field labels', () => {
  it('shows a beneficiaryGroup error under the Payee Label name', () => {
    const showMessage = vi.fn();

    showApiErrorMessages(
      {
        body: {
          beneficiaryGroup: ['Only active Payee Label can be used in Program.'],
        },
      },
      showMessage,
    );

    expect(showMessage).toHaveBeenCalledWith(
      'Payee Label: Only active Payee Label can be used in Program.',
    );
  });

  it('returns a beneficiary_group error under the Payee Label name', () => {
    const message = getApiErrorMessages({
      body: {
        beneficiary_group: [
          'Payee Label does not belong to the selected Payee Type.',
        ],
      },
    });

    expect(message).toBe(
      'Payee Label: Payee Label does not belong to the selected Payee Type.',
    );
  });

  it('keeps the generic label for other fields', () => {
    const message = getApiErrorMessages({
      body: {
        data_collecting_type: ['Data Collecting Type has no Payee Type.'],
      },
    });

    expect(message).toBe(
      'Data Collecting Type: Data Collecting Type has no Payee Type.',
    );
  });
});
