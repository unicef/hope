import React from 'react';
import { useTranslation } from 'react-i18next';
import { Template } from './PeriodicDataUpdatesTemplatesList';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  DialogActions,
  Button,
} from '@mui/material';
import { LabelizedField } from '@components/core/LabelizedField';
import { fetchPeriodicDataUpdateTemplateDetails } from '@api/periodicDataUpdateApi';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useQuery } from '@tanstack/react-query';
import { LoadingComponent } from '@components/core/LoadingComponent';

interface PeriodicDataUpdatesTemplateDetailsDialogProps {
  open: boolean;
  onClose: () => void;
  template: Template;
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

  if (isLoading) return <LoadingComponent />;

  return (
    <Dialog open={open} onClose={onClose} scroll="paper" data-cy="periodic-data-update-detail">
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
                  <TableCell data-cy={`template-field-${index}`}>{roundData.field}</TableCell>
                  <TableCell data-cy={`template-round-number-${index}`}>{roundData.round}</TableCell>
                  <TableCell data-cy={`template-round-name-${index}`}>{roundData.round_name}</TableCell>
                  <TableCell data-cy={`template-number-of-individuals-${index}`}>
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
