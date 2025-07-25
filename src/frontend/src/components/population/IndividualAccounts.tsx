import { DividerLine } from '@components/core/DividerLine';
import { LabelizedField } from '@components/core/LabelizedField';
import { Title } from '@core/Title';
import { usePermissions } from '@hooks/usePermissions';
import { Grid2 as Grid, Paper, Theme, Typography } from '@mui/material';
import { IndividualDetail } from '@restgenerated/models/IndividualDetail';
import { renderSomethingOrDash } from '@utils/utils';
import { t } from 'i18next';
import { FC } from 'react';
import { hasPermissions, PERMISSIONS } from 'src/config/permissions';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';

interface IndividualAccountsProps {
  individual: IndividualDetail;
}

const Overview = styled(Paper)<{ theme?: Theme }>`
  padding: ${({ theme }) => theme.spacing(8)}
    ${({ theme }) => theme.spacing(11)};
  margin-top: ${({ theme }) => theme.spacing(6)};
  margin-bottom: ${({ theme }) => theme.spacing(4)};
`;

export const IndividualAccounts: FC<IndividualAccountsProps> = ({
  individual,
}) => {
  const permissions = usePermissions();
  const canViewDeliveryMechanisms = hasPermissions(
    PERMISSIONS.POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION,
    permissions,
  );
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;

  if (!individual?.accounts?.length || !canViewDeliveryMechanisms) {
    return null;
  }
  return (
    <Overview>
      <Title>
        <Typography variant="h6">
          {t(`${beneficiaryGroup?.memberLabel} Accounts`)}
        </Typography>
      </Title>
      <Grid container spacing={6}>
        {individual.accounts.map((mechanism, index) => {
          const tabData = JSON.parse(mechanism.data);
          return (
            <Grid size={{ xs: 12 }} key={index}>
              <Typography variant="h6">{mechanism.accountType}</Typography>
              <Grid container spacing={3}>
                {Object.entries(tabData).map(([key, value], idx) => (
                  <Grid key={idx} size={{ xs: 3 }}>
                    <LabelizedField label={key.replace(/_/g, ' ')}>
                      {renderSomethingOrDash(value)}
                    </LabelizedField>
                  </Grid>
                ))}
              </Grid>
              {index < individual.accounts.length - 1 && <DividerLine />}
            </Grid>
          );
        })}
      </Grid>
    </Overview>
  );
};
