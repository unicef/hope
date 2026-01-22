import EditIcon from '@mui/icons-material/Edit';
import { Box, Grid } from '@mui/material';
import { ReactElement } from 'react';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { ContentLink } from '@components/core/ContentLink';
import { useProgramContext } from 'src/programContext';
import { BlueText, LightGrey, StyledBox } from '../LookUpStyles';
import { GrievanceTicketDetail } from '@restgenerated/models/GrievanceTicketDetail';

export function LookUpReassignRoleDisplay({
  selectedHousehold,
  selectedIndividual,
  setLookUpDialogOpen,
  disabled,
}: {
  selectedHousehold?:
    | GrievanceTicketDetail['household']
    | GrievanceTicketDetail['individual']['rolesInHouseholds'][number]['household'];
  selectedIndividual;
  setLookUpDialogOpen;
  disabled?: boolean;
}): ReactElement {
  const { baseUrl } = useBaseUrl();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  return (
    <StyledBox>
      <Grid container>
        <Grid>
          <Box display="flex" flexDirection="column">
            <span>
              {`${beneficiaryGroup?.groupLabel} ID: `}
              {selectedHousehold?.unicefId ? (
                <ContentLink
                  href={`/${baseUrl}/population/household/${selectedHousehold.id}`}
                >
                  <BlueText> {selectedHousehold.unicefId}</BlueText>
                </ContentLink>
              ) : (
                <BlueText> -</BlueText>
              )}
            </span>
            <span>
              {`${beneficiaryGroup?.memberLabel} ID: `}
              {selectedIndividual?.unicefId ? (
                <ContentLink
                  href={`/${baseUrl}/population/individuals/${selectedIndividual.id}`}
                >
                  <BlueText>{selectedIndividual.unicefId}</BlueText>
                </ContentLink>
              ) : (
                <BlueText>-</BlueText>
              )}
            </span>
          </Box>
        </Grid>
        <Grid>
          <Box p={2}>
            <Grid container justifyContent="center" alignItems="center">
              <Grid>
                {disabled ? null : (
                  <LightGrey>
                    <EditIcon
                      color="inherit"
                      fontSize="small"
                      onClick={() => setLookUpDialogOpen(true)}
                    />
                  </LightGrey>
                )}
              </Grid>
            </Grid>
          </Box>
        </Grid>
      </Grid>
    </StyledBox>
  );
}
