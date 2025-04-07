import { DividerLine } from '@components/core/DividerLine';
import { IndividualNode } from '@generated/graphql';
import { Grid2 as Grid, Paper, Typography } from '@mui/material';
import { Title } from '@core/Title';
import { t } from 'i18next';
import React, { FC } from 'react';
import styled from 'styled-components';
import { LabelizedField } from '@components/core/LabelizedField';
import { renderSomethingOrDash } from '@utils/utils';
import { usePermissions } from '@hooks/usePermissions';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from 'src/programContext';

interface IndividualDeliveryMechanismsProps {
  individual: IndividualNode;
}

const Overview = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
  margin-top: ${({ theme }) => theme.spacing(6)};
  margin-bottom: ${({ theme }) => theme.spacing(4)};
`;

export const IndividualDeliveryMechanisms: FC<
  IndividualDeliveryMechanismsProps
> = ({ individual }) => {
  const permissions = usePermissions();
  const canViewDeliveryMechanisms = hasPermissions(
    PERMISSIONS.POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION,
    permissions,
  );
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  if (
    !individual?.deliveryMechanismsData?.length ||
    !canViewDeliveryMechanisms
  ) {
    return null;
  }
  return (
    <Overview>
      <Title>
        <Typography variant="h6">
          {t(`${beneficiaryGroup?.memberLabel} Delivery Mechanisms`)}
        </Typography>
      </Title>
      <Grid container spacing={6}>
        {individual.deliveryMechanismsData.map((mechanism, index) => {
          const tabData = JSON.parse(mechanism.individualTabData);
          return (
            <Grid size={{ xs: 12 }} key={index}>
              <Typography variant="h6">{mechanism.name}</Typography>
              <Grid container spacing={3}>
                {Object.entries(tabData).map(([key, value], idx) => (
                  <Grid key={idx} size={{ xs: 3 }}>
                    <LabelizedField label={key.replace(/_/g, ' ')}>
                      {renderSomethingOrDash(value)}
                    </LabelizedField>
                  </Grid>
                ))}
              </Grid>
              {index < individual.deliveryMechanismsData.length - 1 && (
                <DividerLine />
              )}
            </Grid>
          );
        })}
      </Grid>
    </Overview>
  );
};
