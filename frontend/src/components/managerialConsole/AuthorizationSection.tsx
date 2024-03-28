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
import { AuthorizePaymentPlansModal } from '@components/managerialConsole/AuthorizePaymentPlansModal';

interface AuthorizationSectionProps {
  selectedAuthorized: any[];
  setSelectedAuthorized: (value: React.SetStateAction<any[]>) => void;
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
  inAuthorizationData: any;
  bulkAction: any;
}

export const AuthorizationSection: React.FC<AuthorizationSectionProps> = ({
  selectedAuthorized,
  setSelectedAuthorized,
  handleSelect,
  handleSelectAll,
  inAuthorizationData,
  bulkAction,
}) => {
  const { t } = useTranslation();
  const handleSelectAllAuthorized = () =>
    handleSelectAll(inAuthorizationData, setSelectedAuthorized);
  return (
    <BaseSection
      title={t('Payment Plans pending for Authorization')}
      buttons={
        <AuthorizePaymentPlansModal
          selectedPlans={selectedAuthorized}
          onAuthorize={(_, comment) => {
            return bulkAction.mutateAsync({
              ids: selectedAuthorized,
              action: 'AUTHORIZE',
              comment: comment,
            });
          }}
        />
      }
    >
      <Table>
        <TableHead>
          <TableRow>
            <TableCell padding="checkbox">
              <Checkbox onClick={handleSelectAllAuthorized} />
            </TableCell>
            <TableCell>{t('Payment Plan ID')}</TableCell>
            <TableCell>{t('Status')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {inAuthorizationData?.results?.map((plan: any) => (
            <TableRow key={plan.id}>
              <TableCell padding="checkbox">
                <Checkbox
                  checked={selectedAuthorized.includes(plan.id)}
                  onChange={() =>
                    handleSelect(
                      selectedAuthorized,
                      setSelectedAuthorized,
                      plan,
                    )
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
