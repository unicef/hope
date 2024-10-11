import { Box } from '@mui/material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import { IndividualNode, IndividualQuery } from '@generated/graphql';
import { FlagTooltip } from '@core/FlagTooltip';
import { WarningTooltip } from '@core/WarningTooltip';

interface IndividualFlagsProps {
  individual: IndividualQuery['individual'] | IndividualNode;
}

export const IndividualFlags: React.FC<IndividualFlagsProps> = ({
  individual,
}) => {
  const { t } = useTranslation();

  const getDuplicateTooltip = (individualObject): React.ReactElement => {
    if (individualObject?.status === 'DUPLICATE') {
      return <WarningTooltip data-cy="tooltip-confirmed-duplicate" confirmed message={t('Confirmed Duplicate')} />;
    }
    if (individualObject?.deduplicationGoldenRecordStatus !== 'UNIQUE') {
      return <WarningTooltip data-cy="tooltip-possible-duplicate" message={t('Possible Duplicate')} />;
    }
    return null;
  };

  const getSanctionListPossibleMatchTooltip = (
    individualObject,
  ): React.ReactElement => {
    if (individualObject?.sanctionListPossibleMatch) {
      return <FlagTooltip data-cy="tooltip-sanction-list-possible" message={t('Sanction List Possible Match')} />;
    }
    return null;
  };

  const getSanctionListConfirmedMatchTooltip = (
    individualObject,
  ): React.ReactElement => {
    if (individualObject?.sanctionListConfirmedMatch) {
      return (
        <FlagTooltip data-cy="sanction-list-confirmed" message={t('Sanction List Confirmed Match')} confirmed />
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