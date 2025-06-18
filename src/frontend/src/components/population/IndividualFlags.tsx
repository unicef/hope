import { Box } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { FlagTooltip } from '@core/FlagTooltip';
import { WarningTooltip } from '@core/WarningTooltip';
import { FC, ReactElement } from 'react';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';

interface IndividualFlagsProps {
  individual: IndividualDetail;
}

export const IndividualFlags: FC<IndividualFlagsProps> = ({ individual }) => {
  const { t } = useTranslation();

  const getDuplicateTooltip = (individualObject): ReactElement => {
    if (individualObject?.status === 'DUPLICATE') {
      return (
        <WarningTooltip
          data-cy="tooltip-confirmed-duplicate"
          confirmed
          message={t('Confirmed Duplicate')}
        />
      );
    }
    if (individualObject?.deduplicationGoldenRecordStatus !== 'UNIQUE') {
      return (
        <WarningTooltip
          data-cy="tooltip-possible-duplicate"
          message={t('Possible Duplicate')}
        />
      );
    }
    return null;
  };

  const getSanctionListPossibleMatchTooltip = (
    individualObject,
  ): ReactElement => {
    if (individualObject?.sanctionListPossibleMatch) {
      return (
        <FlagTooltip
          data-cy="tooltip-sanction-list-possible"
          message={t('Sanction List Possible Match')}
        />
      );
    }
    return null;
  };

  const getSanctionListConfirmedMatchTooltip = (
    individualObject,
  ): ReactElement => {
    if (individualObject?.sanctionListConfirmedMatch) {
      return (
        <FlagTooltip
          data-cy="sanction-list-confirmed"
          message={t('Sanction List Confirmed Match')}
          confirmed
        />
      );
    }
    return null;
  };

  return (
    <>
      <Box mr={2}>{getDuplicateTooltip(individual)}</Box>
      <Box mr={2}>{getSanctionListPossibleMatchTooltip(individual)}</Box>
      <Box mr={2}>{getSanctionListConfirmedMatchTooltip(individual)}</Box>
    </>
  );
};
