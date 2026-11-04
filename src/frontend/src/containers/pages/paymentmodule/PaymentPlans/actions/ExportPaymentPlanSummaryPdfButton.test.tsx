import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { TestProviders } from 'src/testUtils/testProviders';
import { PaymentPlanStatusEnum } from '@restgenerated/models/PaymentPlanStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { PERMISSIONS } from '../../../../../config/permissions';
import type { PaymentPlanDetail } from '../types';
import { ExportPaymentPlanSummaryPdfButton } from './ExportPaymentPlanSummaryPdfButton';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    businessArea: 'afghanistan',
    programId: 'test-program',
    baseUrl: 'afghanistan/test-program',
  }),
}));

vi.mock('../../../../../programContext', () => ({
  useProgramContext: () => ({ isActiveProgram: true }),
}));

const mockUsePermissions = vi.hoisted(() =>
  vi.fn((): string[] => [PERMISSIONS.PM_EXPORT_PDF_SUMMARY]),
);

vi.mock('@hooks/usePermissions', () => ({
  usePermissions: mockUsePermissions,
}));

const mockShowMessage = vi.hoisted(() => vi.fn());

vi.mock('@hooks/useSnackBar', async (importOriginal) => ({
  ...(await importOriginal<typeof import('@hooks/useSnackBar')>()),
  useSnackbar: () => ({ showMessage: mockShowMessage }),
}));

const renderButton = (
  status: PaymentPlanStatusEnum,
  exportPdfFileSummary: string | null = null,
) =>
  render(
    <ExportPaymentPlanSummaryPdfButton
      paymentPlan={
        {
          id: 'group-1',
          status,
          exportPdfFileSummary,
        } as PaymentPlanDetail
      }
    />,
    { wrapper: TestProviders },
  );

describe('ExportGroupSummaryPdfButton', () => {
  beforeEach(() => {
    mockUsePermissions.mockReturnValue([PERMISSIONS.PM_EXPORT_PDF_SUMMARY]);
    mockShowMessage.mockClear();
  });

  it('shows nothing without the export permission', () => {
    mockUsePermissions.mockReturnValue([]);
    const { container } = renderButton(PaymentPlanStatusEnum.ACCEPTED);
    expect(container.innerHTML).toBe('');
  });

  it('shows nothing before review when no summary exists', () => {
    const { container } = renderButton(PaymentPlanStatusEnum.OPEN);
    expect(container.innerHTML).toBe('');
  });

  it('offers to generate the summary for an accepted payment plan', () => {
    renderButton(PaymentPlanStatusEnum.ACCEPTED);
    expect(
      screen.getByTestId('button-export-group-summary-pdf').textContent,
    ).toBe('Generate Payment Plan Summary');
    expect(
      screen.queryByTestId('button-download-group-summary-pdf'),
    ).toBeNull();
  });

  it('offers download and regenerate once the summary exists', () => {
    renderButton(PaymentPlanStatusEnum.FINISHED, '/media/summary.pdf');
    expect(
      screen
        .getByTestId('button-download-group-summary-pdf')
        .getAttribute('href'),
    ).toBe('/media/summary.pdf');
    expect(
      screen.getByTestId('button-export-group-summary-pdf').textContent,
    ).toBe('Regenerate Payment Plan Summary');
  });

  it('keeps only the download for a closed payment plan', () => {
    renderButton(PaymentPlanStatusEnum.CLOSED, '/media/summary.pdf');
    expect(
      screen.getByTestId('button-download-group-summary-pdf'),
    ).not.toBeNull();
    expect(screen.queryByTestId('button-export-group-summary-pdf')).toBeNull();
  });

  it('starts generating the summary', async () => {
    const exportSpy = vi
      .spyOn(
        RestService,
        'restBusinessAreasProgramsPaymentPlansExportPdfPaymentPlanSummaryRetrieve',
      )
      .mockResolvedValue({} as never);
    renderButton(PaymentPlanStatusEnum.IN_REVIEW);

    fireEvent.click(screen.getByTestId('button-export-group-summary-pdf'));

    await waitFor(() =>
      expect(exportSpy).toHaveBeenCalledWith({
        businessAreaSlug: 'afghanistan',
        programCode: 'test-program',
        id: 'group-1',
      }),
    );
    expect(mockShowMessage).toHaveBeenCalledWith(
      'Payment Plan Summary is being generated.',
    );
  });
});
