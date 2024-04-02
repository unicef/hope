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
import { useSnackbar } from '@hooks/useSnackBar';

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
  const { showMessage } = useSnackbar();
  const handleSelectAllApproved = () => {
    const ids = inApprovalData.results.map((plan) => plan.id);
    handleSelectAll(ids, selectedApproved, setSelectedApproved);
  };

  const allSelected = inApprovalData?.results?.every((plan) =>
    selectedApproved.includes(plan.id),
  );

  const selectedPlansUnicefIds = inApprovalData?.results
    .filter((plan) => selectedApproved.includes(plan.id))
    .map((plan) => plan.unicef_id);

  return (
    <BaseSection
      title={t('Payment Plans pending for Approval')}
      buttons={
        <ApprovePaymentPlansModal
          selectedPlansIds={selectedApproved}
          selectedPlansUnicefIds={selectedPlansUnicefIds}
          onApprove={async (_, comment) => {
            try {
              await bulkAction.mutateAsync({
                ids: selectedApproved,
                action: 'APPROVE',
                comment: comment,
              });
              showMessage(t('Payment Plan(s) Approved'));
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
            <TableCell padding="checkbox">
              <Checkbox
                checked={allSelected && selectedApproved.length > 0}
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
                  checked={selectedApproved.includes(plan.id)}
                  onChange={() =>
                    handleSelect(selectedApproved, setSelectedApproved, plan.id)
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
