import React from 'react';
import { BaseSection } from '@components/core/BaseSection';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Checkbox,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { ReleasePaymentPlansModal } from '@components/managerialConsole/ReleasePaymentPlansModal';
import { UniversalMoment } from '@components/core/UniversalMoment';

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
          onRelease={(_, comment) =>
            bulkAction.mutateAsync({
              ids: selectedInReview,
              action: 'REVIEW',
              comment: comment,
            })
          }
        />
      }
    >
      <Table>
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox">
              <Checkbox
                checked={allSelected && selectedInReview.length > 0}
                onClick={handleSelectAllReviewed}
              />
            </TableCell>
            <TableCell>{t('Payment Plan ID')}</TableCell>
            <TableCell>{t('Programme Name')}</TableCell>
            <TableCell>{t('Last Modified Date')}</TableCell>
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
              <TableCell>{plan.unicef_id}</TableCell>
              <TableCell>{plan.program}</TableCell>
              <TableCell>
                <UniversalMoment>
                  {plan.last_approval_process_date}
                </UniversalMoment>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </BaseSection>
  );
};
