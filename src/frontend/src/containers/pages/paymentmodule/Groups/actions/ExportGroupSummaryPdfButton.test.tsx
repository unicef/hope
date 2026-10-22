import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { TestProviders } from 'src/testUtils/testProviders';
import { PaymentPlanGroupStatusEnum } from '@restgenerated/models/PaymentPlanGroupStatusEnum';
import { RestService } from '@restgenerated/services/RestService';
import { PERMISSIONS } from '../../../../../config/permissions';
import type { PaymentPlanGroupDetail } from '../types';
import { ExportGroupSummaryPdfButton } from './ExportGroupSummaryPdfButton';

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
  status: PaymentPlanGroupStatusEnum,
  exportPdfFileSummary: string | null = null,
) =>
  render(
    <ExportGroupSummaryPdfButton
      group={
        {
          id: 'group-1',
          status,
          exportPdfFileSummary,
        } as PaymentPlanGroupDetail
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
    const { container } = renderButton(PaymentPlanGroupStatusEnum.ACCEPTED);
    expect(container.innerHTML).toBe('');
  });

  it('shows nothing before review when no summary exists', () => {
    const { container } = renderButton(PaymentPlanGroupStatusEnum.OPEN);
    expect(container.innerHTML).toBe('');
  });

  it('offers to generate the summary for an accepted group', () => {
    renderButton(PaymentPlanGroupStatusEnum.ACCEPTED);
    expect(
      screen.getByTestId('button-export-group-summary-pdf').textContent,
    ).toBe('Generate Payment Plan Summary');
    expect(
      screen.queryByTestId('button-download-group-summary-pdf'),
    ).toBeNull();
  });

  it('offers download and regenerate once the summary exists', () => {
    renderButton(PaymentPlanGroupStatusEnum.FINISHED, '/media/summary.pdf');
    expect(
      screen
        .getByTestId('button-download-group-summary-pdf')
        .getAttribute('href'),
    ).toBe('/media/summary.pdf');
    expect(
      screen.getByTestId('button-export-group-summary-pdf').textContent,
    ).toBe('Regenerate Payment Plan Summary');
  });

  it('keeps only the download for a closed group', () => {
    renderButton(PaymentPlanGroupStatusEnum.CLOSED, '/media/summary.pdf');
    expect(
      screen.getByTestId('button-download-group-summary-pdf'),
    ).not.toBeNull();
    expect(screen.queryByTestId('button-export-group-summary-pdf')).toBeNull();
  });

  it('starts generating the summary', async () => {
    const exportSpy = vi
      .spyOn(
        RestService,
        'restBusinessAreasProgramsPaymentPlanGroupsExportPdfPaymentPlanSummaryRetrieve',
      )
      .mockResolvedValue({} as never);
    renderButton(PaymentPlanGroupStatusEnum.IN_REVIEW);

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
