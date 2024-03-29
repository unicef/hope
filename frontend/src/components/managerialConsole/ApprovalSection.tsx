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
import { ApprovePaymentPlansModal } from '@components/managerialConsole/ApprovePaymentPlansModal';
import { UniversalMoment } from '@components/core/UniversalMoment';

interface ApprovalSectionProps {
  selectedApproved: any[];
  setSelectedApproved: (value: React.SetStateAction<any[]>) => void;
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
  inApprovalData: any;
  bulkAction: any;
}

export const ApprovalSection: React.FC<ApprovalSectionProps> = ({
  selectedApproved,
  setSelectedApproved,
  handleSelect,
  handleSelectAll,
  inApprovalData,
  bulkAction,
}) => {
  const { t } = useTranslation();
  const handleSelectAllApproved = () => {
    const ids = inApprovalData.results.map((plan) => plan.id);
    handleSelectAll(ids, selectedApproved, setSelectedApproved);
  };

  const allSelected = inApprovalData?.results?.every((plan) =>
    selectedApproved.includes(plan.id),
  );

  return (
    <BaseSection
      title={t('Payment Plans pending for Approval')}
      buttons={
        <ApprovePaymentPlansModal
          selectedPlans={selectedApproved}
          onApprove={(_, comment) =>
            bulkAction.mutateAsync({
              ids: selectedApproved,
              action: 'APPROVE',
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
                checked={allSelected === selectedApproved.length > 0}
                onClick={handleSelectAllApproved}
              />
            </TableCell>
            <TableCell>{t('Payment Plan ID')}</TableCell>
            <TableCell>{t('Programme Name')}</TableCell>
            <TableCell>{t('Last Modified Date')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {inApprovalData?.results?.map((plan: any) => (
            <TableRow key={plan.id}>
              <TableCell padding="checkbox">
                <Checkbox
                  checked={selectedApproved.some(
                    (selectedPlan) => selectedPlan.id === plan.id,
                  )}
                  onChange={() =>
                    handleSelect(selectedApproved, setSelectedApproved, plan.id)
                  }
                />
              </TableCell>
              <TableCell>{plan.unicef_id}</TableCell>
              <TableCell>{plan.program.name}</TableCell>
              <TableCell>
                <UniversalMoment>{plan.last_modified_date}</UniversalMoment>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </BaseSection>
  );
};
