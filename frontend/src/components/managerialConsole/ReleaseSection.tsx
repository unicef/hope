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

interface ReleaseSectionProps {
  selectedInReview: any[];
  setSelectedInReview: (value: React.SetStateAction<any[]>) => void;
  handleSelect: (
    selected: any[],
    setSelected: (value: React.SetStateAction<any[]>) => void,
    id: any,
  ) => void;
  handleSelectAll: (
    items: any[],
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
  inReviewData,
  bulkAction,
}) => {
  const { t } = useTranslation();

  return (
    <BaseSection
      title={t('Payment Plans pending for Release')}
      buttons={
        <ReleasePaymentPlansModal
          selectedPlans={selectedInReview}
          onRelease={(_, comment) =>
            bulkAction.mutateAsync({
              ids: selectedInReview,
              action: 'RELEASE',
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
              <Checkbox />
            </TableCell>
            <TableCell>{t('Payment Plan ID')}</TableCell>
            <TableCell>{t('Status')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {inReviewData?.results?.map((plan: any) => (
            <TableRow key={plan.id}>
              <TableCell padding="checkbox">
                <Checkbox
                  checked={selectedInReview.some(
                    (selectedPlan) => selectedPlan.id === plan.id,
                  )}
                  onChange={() =>
                    handleSelect(selectedInReview, setSelectedInReview, plan)
                  }
                />
              </TableCell>
              <TableCell>{plan.unicef_id}</TableCell>
              <TableCell>{plan.status}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </BaseSection>
  );
};
