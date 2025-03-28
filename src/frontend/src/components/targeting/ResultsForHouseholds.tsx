import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid2 as Grid,
  List,
  ListItem,
  Typography,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { PaymentPlanBuildStatus } from '@generated/graphql';
import { MiśTheme } from '../../theme';
import { FieldBorder } from '@core/FieldBorder';
import { LabelizedField } from '@core/LabelizedField';
import { PaperContainer } from './PaperContainer';
import { useProgramContext } from 'src/programContext';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { PaymentPlanDetail } from '@restgenerated/models/PaymentPlanDetail';
import { Pointer } from '@components/core/Pointer';
import { ReactElement, useState } from 'react';

const colors = {
  femaleChildren: '#5F02CF',
  maleChildren: '#1D6A64',
  femaleAdult: '#DFCCF5',
  maleAdult: '#B1E3E0',
};

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(2)};
`;

const ContentWrapper = styled.div`
  display: flex;
`;

const SummaryBorder = styled.div`
  padding: ${({ theme }) => theme.spacing(4)};
  border-color: #b1b1b5;
  border-left-width: 1px;
  border-left-style: solid;
`;

const SummaryValue = styled.div`
  font-family: ${({ theme }: { theme: MiśTheme }) =>
    theme.hctTypography.fontFamily};
  color: #253b46;
  font-size: 36px;
  line-height: 32px;
  margin-top: ${({ theme }) => theme.spacing(2)};
`;

interface ResultsProps {
  targetPopulation: PaymentPlanDetail;
}

function ResultsForHouseholds({
  targetPopulation,
}: ResultsProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiary_group;
  const [openDialog, setOpenDialog] = useState(false);
  const handleOpen = () => {
    if (targetPopulation?.failed_wallet_validation_collectors_ids?.length > 0) {
      setOpenDialog(true);
    }
  };
  const handleClose = () => setOpenDialog(false);

  if (targetPopulation.build_status !== PaymentPlanBuildStatus.Ok) {
    return null;
  }

  return (
    <div>
      <PaperContainer>
        <Title>
          <Typography variant="h6">{t('Results')}</Typography>
        </Title>
        <ContentWrapper>
          <Grid container>
            <Grid size={{ xs: 4 }}>
              <Grid container spacing={0} justifyContent="flex-start">
                <Grid size={{ xs: 6 }}>
                  <FieldBorder color={colors.femaleChildren}>
                    <LabelizedField
                      label={t('Female Children')}
                      value={targetPopulation.female_children_count}
                    />
                  </FieldBorder>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <FieldBorder color={colors.femaleAdult}>
                    <LabelizedField
                      label={t('Female Adults')}
                      value={targetPopulation.female_adults_count}
                    />
                  </FieldBorder>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <FieldBorder color={colors.maleChildren}>
                    <LabelizedField
                      label={t('Male Children')}
                      value={targetPopulation.male_children_count}
                    />
                  </FieldBorder>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <FieldBorder color={colors.maleAdult}>
                    <LabelizedField
                      label={t('Male Adults')}
                      value={targetPopulation.male_adults_count}
                    />
                  </FieldBorder>
                </Grid>
              </Grid>
            </Grid>
            <Grid size={{ xs: 4 }}>
              <Grid
                container
                spacing={0}
                justifyContent="flex-start"
                alignItems="center"
              >
                <Grid size={{ xs: 6 }}>
                  <SummaryBorder>
                    <>
                      <LabelizedField
                        label={t(
                          'Collectors failed payment channel validation',
                        )}
                      >
                        <SummaryValue
                          onClick={() => handleOpen()}
                          data-cy="total-collectors-failed-count"
                        >
                          <Pointer>
                            {targetPopulation
                              ?.failed_wallet_validation_collectors_ids
                              ?.length || '-'}
                          </Pointer>
                        </SummaryValue>
                      </LabelizedField>
                      <Dialog open={openDialog} onClose={handleClose}>
                        <DialogTitle>View IDs</DialogTitle>
                        <DialogContent>
                          <List>
                            {targetPopulation?.failed_wallet_validation_collectors_ids?.map(
                              (id, index) => (
                                <ListItem key={index}>{id}</ListItem>
                              ),
                            )}
                          </List>
                        </DialogContent>
                        <DialogActions>
                          <Button onClick={handleClose} color="primary">
                            Close
                          </Button>
                        </DialogActions>
                      </Dialog>
                    </>
                  </SummaryBorder>
                </Grid>

                {/* <Grid item xs={4}>
                  <ChartContainer>
                    <Pie
                      width={100}
                      height={100}
                      options={{
                        plugins: {
                          legend: {
                            display: false,
                          },
                        },
                      }}
                      data={{
                        labels: [
                          t('Female Children'),
                          t('Female Adults'),
                          t('Male Children'),
                          t('Male Adults'),
                        ],
                        datasets: [
                          {
                            data: [
                              targetPopulation.femaleChildrenCount,
                              targetPopulation.femaleAdultsCount,
                              targetPopulation.maleChildrenCount,
                              targetPopulation.maleAdultsCount,
                            ],
                            backgroundColor: [
                              colors.femaleChildren,
                              colors.femaleAdult,
                              colors.maleChildren,
                              colors.maleAdult,
                            ],
                          },
                        ],
                      }}
                    />
                  </ChartContainer>
                </Grid> */}
              </Grid>
            </Grid>
            <Grid size={{ xs: 4 }}>
              <Grid container spacing={0} justifyContent="flex-end">
                <Grid size={{ xs: 6 }}>
                  <SummaryBorder>
                    <LabelizedField
                      label={`Total Number of ${beneficiaryGroup?.group_label_plural}`}
                    >
                      <SummaryValue data-cy="total-number-of-households-count">
                        {targetPopulation.total_households_count || '0'}
                      </SummaryValue>
                    </LabelizedField>
                  </SummaryBorder>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <SummaryBorder>
                    <LabelizedField
                      label={`Targeted ${beneficiaryGroup?.member_label_plural}`}
                    >
                      <SummaryValue>
                        {targetPopulation.total_individuals_count || '0'}
                      </SummaryValue>
                    </LabelizedField>
                  </SummaryBorder>
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </ContentWrapper>
      </PaperContainer>
    </div>
  );
}

export default withErrorBoundary(ResultsForHouseholds, 'ResultsForHouseholds');
