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
import { PeriodicDataUpdateTemplateDetail } from '@restgenerated/models/PeriodicDataUpdateTemplateDetail';
import { PeriodicDataUpdateTemplateList } from '@restgenerated/models/PeriodicDataUpdateTemplateList';
import { RestService } from '@restgenerated/services/RestService';
import { useQuery } from '@tanstack/react-query';
import { FC } from 'react';
import { useTranslation } from 'react-i18next';

interface PeriodicDataUpdatesTemplateDetailsDialogProps {
  open: boolean;
  onClose: () => void;
  template: PeriodicDataUpdateTemplateList;
}

export const PeriodicDataUpdatesTemplateDetailsDialog: FC<
  PeriodicDataUpdatesTemplateDetailsDialogProps
> = ({ open, onClose, template }) => {
  const { t } = useTranslation();
  const { businessArea, programId } = useBaseUrl();
  const { data: templateDetailsData, isLoading } =
    useQuery<PeriodicDataUpdateTemplateDetail>({
      queryKey: [
        'periodicDataUpdateTemplateDetails',
        businessArea,
        programId,
        template.id,
      ],

      queryFn: () =>
        RestService.restBusinessAreasProgramsPeriodicDataUpdateTemplatesRetrieve(
          {
            businessAreaSlug: businessArea,
            id: template.id,
            programSlug: programId,
          },
        ),
    });
  const { data: periodicFieldsData, isLoading: periodicFieldsLoading } =
    useQuery({
      queryKey: ['periodicFields', businessArea, programId],
      queryFn: () =>
        RestService.restBusinessAreasProgramsPeriodicFieldsList({
          businessAreaSlug: businessArea,
          programSlug: programId,
        }),
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
              {templateDetailsData?.roundsData?.map((roundData, index) => (
                <TableRow key={index}>
                  <TableCell data-cy={`template-field-${index}`}>
                    {typeof pduDataDict[roundData.field]?.label === 'object'
                      ? pduDataDict[roundData.field]?.label.englishEn ||
                        roundData.field
                      : pduDataDict[roundData.field]?.label || roundData.field}
                  </TableCell>
                  <TableCell data-cy={`template-round-number-${index}`}>
                    {roundData.round}
                  </TableCell>
                  <TableCell data-cy={`template-round-name-${index}`}>
                    {roundData.roundName}
                  </TableCell>
                  <TableCell
                    data-cy={`template-number-of-individuals-${index}`}
                  >
                    {roundData.numberOfRecords}
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
