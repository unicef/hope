import React from 'react';
import { BaseSection } from '@components/core/BaseSection';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Checkbox,
  Box,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { ReleasePaymentPlansModal } from '@components/managerialConsole/ReleasePaymentPlansModal';
import { UniversalMoment } from '@components/core/UniversalMoment';
import { useSnackbar } from '@hooks/useSnackBar';
import { BlackLink } from '@components/core/BlackLink';
import { useBaseUrl } from '@hooks/useBaseUrl';

interface ReleaseSectionProps {
  selectedInReview: any[];
  setSelectedInReview: (value: React.SetStateAction<any[]>) => void;
  handleSelect: (
    selected: any[],
    setSelected: (value: React.SetStateAction<any[]>) => void,
    id: any,
  ) => void;
  handleSelectAll: (
    ids: any[],
    selected: any[],
    setSelected: {
      (value: React.SetStateAction<any[]>): void;
      (arg0: any[]): void;
    },
  ) => void;
  inReviewData: any;
  bulkAction: any;
}

export const ReleaseSection: React.FC<ReleaseSectionProps> = ({
  selectedInReview,
  setSelectedInReview,
  handleSelect,
  handleSelectAll,
  inReviewData,
  bulkAction,
}) => {
  const { t } = useTranslation();
  const { businessArea } = useBaseUrl();
  const { showMessage } = useSnackbar();
  const handleSelectAllReviewed = () => {
    const ids = inReviewData?.results?.map((plan) => plan.id);
    handleSelectAll(ids, selectedInReview, setSelectedInReview);
  };
  const allSelected = inReviewData?.results?.every((plan) =>
    selectedInReview.includes(plan.id),
  );

  const selectedPlansUnicefIds = inReviewData?.results
    .filter((plan) => selectedInReview.includes(plan.id))
    .map((plan) => plan.unicef_id);

  return (
    <BaseSection
      title={t('Payment Plans pending for Release')}
      buttons={
        <ReleasePaymentPlansModal
          selectedPlansIds={selectedInReview}
          selectedPlansUnicefIds={selectedPlansUnicefIds}
          onRelease={async (_, comment) => {
            try {
              await bulkAction.mutateAsync({
                ids: selectedInReview,
                action: 'REVIEW',
                comment: comment,
              });
              showMessage(t('Payment Plan(s) Released'));
              setSelectedInReview([]);
            } catch (e) {
              showMessage(e.message);
            }
          }}
        />
      }
    >
      <Table>
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox" style={{ width: '10%' }}>
              <Box sx={{ flex: 1 }}>
                <Checkbox
                  checked={allSelected && selectedInReview.length > 0}
                  onClick={handleSelectAllReviewed}
                />
              </Box>
            </TableCell>
            <TableCell align="left" style={{ width: '22.5%' }}>
              <Box sx={{ flex: 1 }}>{t('Payment Plan ID')}</Box>
            </TableCell>
            <TableCell align="left" style={{ width: '22.5%' }}>
              <Box sx={{ flex: 1 }}>{t('Programme Name')}</Box>
            </TableCell>
            <TableCell align="left" style={{ width: '22.5%' }}>
              <Box sx={{ flex: 1 }}>{t('Last Modified Date')}</Box>
            </TableCell>
            <TableCell align="left" style={{ width: '22.5%' }}>
              <Box sx={{ flex: 1 }}>{t('Authorized by')}</Box>
            </TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {inReviewData?.results?.map((plan: any) => (
            <TableRow key={plan.id}>
              <TableCell padding="checkbox">
                <Checkbox
                  checked={selectedInReview.includes(plan.id)}
                  onChange={() =>
                    handleSelect(selectedInReview, setSelectedInReview, plan.id)
                  }
                />
              </TableCell>
              <TableCell align="left">
                <BlackLink
                  to={`/${businessArea}/programs/${plan.program_id}/payment-module/${plan.isFollowUp ? 'followup-payment-plans' : 'payment-plans'}/${plan.id}`}
                  newTab={true}
                >
                  {plan.unicef_id}
                </BlackLink>
              </TableCell>
              <TableCell align="left">{plan.program}</TableCell>
              <TableCell align="left">
                <UniversalMoment>
                  {plan.last_approval_process_date}
                </UniversalMoment>
              </TableCell>
              <TableCell align="left">
                {plan.last_approval_process_by}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </BaseSection>
  );
};
