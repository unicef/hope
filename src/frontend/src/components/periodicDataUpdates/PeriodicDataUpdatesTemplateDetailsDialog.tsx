import {
  fetchPeriodicDataUpdateTemplateDetails,
  fetchPeriodicFields,
} from '@api/periodicDataUpdateApi';
import { LabelizedField } from '@components/core/LabelizedField';
import { LoadingComponent } from '@components/core/LoadingComponent';
import { useArrayToDict } from '@hooks/useArrayToDict';
import { useBaseUrl } from '@hooks/useBaseUrl';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from '@mui/material';
import { PeriodicDataUpdateTemplateList } from 'restgenerated/models/PeriodicDataUpdateTemplateList';
import { useQuery } from '@tanstack/react-query';
import React from 'react';
import { useTranslation } from 'react-i18next';

interface PeriodicDataUpdatesTemplateDetailsDialogProps {
  open: boolean;
  onClose: () => void;
  template: PeriodicDataUpdateTemplateList;
}

export const PeriodicDataUpdatesTemplateDetailsDialog: React.FC<
  PeriodicDataUpdatesTemplateDetailsDialogProps
> = ({ open, onClose, template }) => {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { data: templateDetailsData, isLoading } = useQuery({
    queryKey: [
      'periodicDataUpdateTemplateDetails',
      businessArea,
      programId,
      template.id,
    ],
    queryFn: () =>
      fetchPeriodicDataUpdateTemplateDetails(
        businessArea,
        programId,
        template.id,
      ),
  });
  const { data: periodicFieldsData, isLoading: periodicFieldsLoading } =
    useQuery({
      queryKey: ['periodicFields', businessArea, programId],
      queryFn: () => fetchPeriodicFields(businessArea, programId),
    });
  const pduDataDict = useArrayToDict(periodicFieldsData?.results, 'name', '*');
  if (isLoading || periodicFieldsLoading || !pduDataDict)
    return <LoadingComponent />;
  return (
    <Dialog
      open={open}
      onClose={onClose}
      scroll="paper"
      data-cy="periodic-data-update-detail"
    >
      <DialogTitle>{t('Periodic Data Updates')}</DialogTitle>
      <DialogContent>
        <LabelizedField label={t('Template Id')}>{template.id}</LabelizedField>
        {templateDetailsData && (
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>{t('Field')}</TableCell>
                <TableCell>{t('Round Number')}</TableCell>
                <TableCell>{t('Round Name')}</TableCell>
                <TableCell>{t('Number of individuals')}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {templateDetailsData?.rounds_data?.map((roundData, index) => (
                <TableRow key={index}>
                  <TableCell data-cy={`template-field-${index}`}>
                    {pduDataDict[roundData.field].label}
                  </TableCell>
                  <TableCell data-cy={`template-round-number-${index}`}>
                    {roundData.round}
                  </TableCell>
                  <TableCell data-cy={`template-round-name-${index}`}>
                    {roundData.round_name}
                  </TableCell>
                  <TableCell
                    data-cy={`template-number-of-individuals-${index}`}
                  >
                    {roundData.number_of_records}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>{t('Close')}</Button>
      </DialogActions>
    </Dialog>
  );
};
