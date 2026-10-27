import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  fireEvent,
  renderWithProviders,
  screen,
  waitFor,
} from 'src/testUtils/testUtils';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { RestService } from '@restgenerated/services/RestService';
import { COMMENT_MAX_LENGTH } from 'src/config';
import { ApprovePaymentPlan } from './ApprovePaymentPlan';

vi.mock('@hooks/useBaseUrl', () => ({
  useBaseUrl: () => ({
    businessArea: 'afghanistan',
    programId: 'test-program',
    baseUrl: 'afghanistan/test-program',
  }),
}));

vi.mock('@hooks/useSnackBar', () => ({
  useSnackbar: () => ({ showMessage: vi.fn() }),
}));

vi.mock('../../../../programContext', () => ({
  useProgramContext: () => ({ isActiveProgram: true }),
}));

vi.mock('@restgenerated/services/RestService', () => ({
  RestService: {
    restBusinessAreasProgramsPaymentPlansApproveCreate: vi.fn(),
    restBusinessAreasProgramsPaymentPlansRetrieve: vi.fn(),
    restBusinessAreasProgramsPaymentPlansList: vi.fn(),
  },
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

const approveMock = vi.mocked(
  RestService.restBusinessAreasProgramsPaymentPlansApproveCreate,
);

function openDialog(): HTMLTextAreaElement {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  renderWithProviders(
    <QueryClientProvider client={queryClient}>
      <ApprovePaymentPlan
        paymentPlan={{ id: 'payment-plan-1', approvalProcess: [] } as any}
      />
    </QueryClientProvider>,
  );
  fireEvent.click(screen.getByTestId('button-approve'));
  return screen.getByLabelText('Comment (optional)') as HTMLTextAreaElement;
}

describe('ApprovePaymentPlan', () => {
  beforeEach(() => {
    approveMock.mockReset();
    approveMock.mockResolvedValue({} as any);
  });

  it('does not approve when Enter is pressed in the comment', async () => {
    const comment = openDialog();
    expect(comment.tagName).toBe('TEXTAREA');
    fireEvent.change(comment, { target: { value: 'first line' } });
    fireEvent.keyPress(comment, { key: 'Enter', code: 'Enter', charCode: 13 });
    fireEvent.keyDown(comment, { key: 'Enter', code: 'Enter' });

    await new Promise((resolve) => setTimeout(resolve, 50));
    expect(approveMock).not.toHaveBeenCalled();
  });

  it('approves with a multi-line comment of max length when the button is clicked', async () => {
    const comment = openDialog();
    const value = `first line\n${'a'.repeat(COMMENT_MAX_LENGTH - 11)}`;
    fireEvent.change(comment, { target: { value } });
    fireEvent.click(screen.getByTestId('button-submit'));

    await waitFor(() => expect(approveMock).toHaveBeenCalledTimes(1));
    expect(approveMock.mock.calls[0][0].requestBody).toEqual({
      comment: value,
    });
  });

  it('clears the comment when the dialog is cancelled', async () => {
    let comment = openDialog();
    fireEvent.change(comment, { target: { value: 'draft comment' } });
    fireEvent.click(screen.getByText('CANCEL'));
    await waitFor(() =>
      expect(screen.queryByLabelText('Comment (optional)')).toBeNull(),
    );

    fireEvent.click(screen.getByTestId('button-approve'));
    comment = screen.getByLabelText(
      'Comment (optional)',
    ) as HTMLTextAreaElement;
    expect(comment.value).toBe('');
  });

  it('keeps the comment when approving fails', async () => {
    approveMock.mockRejectedValue(new Error('failed'));
    const comment = openDialog();
    fireEvent.change(comment, { target: { value: 'keep this comment' } });
    fireEvent.click(screen.getByTestId('button-submit'));

    await waitFor(() => expect(approveMock).toHaveBeenCalledTimes(1));
    await new Promise((resolve) => setTimeout(resolve, 50));
    expect(
      (screen.getByLabelText('Comment (optional)') as HTMLTextAreaElement)
        .value,
    ).toBe('keep this comment');
  });
});
