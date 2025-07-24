import { Pointer } from '@components/core/Pointer';
import withErrorBoundary from '@components/core/withErrorBoundary';
import { FieldBorder } from '@core/FieldBorder';
import { LabelizedField } from '@core/LabelizedField';
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
import { TargetPopulationDetail } from '@restgenerated/models/TargetPopulationDetail';
import { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { MiśTheme } from '../../theme';
import { PaperContainer } from './PaperContainer';

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
  targetPopulation: TargetPopulationDetail;
}

function ResultsForHouseholds({
  targetPopulation,
}: ResultsProps): ReactElement {
  const { t } = useTranslation();
  const { selectedProgram } = useProgramContext();
  const beneficiaryGroup = selectedProgram?.beneficiaryGroup;
  const [openDialog, setOpenDialog] = useState(false);
  const handleOpen = () => {
    if (targetPopulation?.failedWalletValidationCollectorsIds?.length > 0) {
      setOpenDialog(true);
    }
  };
  const handleClose = () => setOpenDialog(false);

  if (targetPopulation.backgroundActionStatus !== null) {
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
                      value={targetPopulation.femaleChildrenCount}
                    />
                  </FieldBorder>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <FieldBorder color={colors.femaleAdult}>
                    <LabelizedField
                      label={t('Female Adults')}
                      value={targetPopulation.femaleAdultsCount}
                    />
                  </FieldBorder>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <FieldBorder color={colors.maleChildren}>
                    <LabelizedField
                      label={t('Male Children')}
                      value={targetPopulation.maleChildrenCount}
                    />
                  </FieldBorder>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <FieldBorder color={colors.maleAdult}>
                    <LabelizedField
                      label={t('Male Adults')}
                      value={targetPopulation.maleAdultsCount}
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
                              ?.failedWalletValidationCollectorsIds?.length ||
                              '-'}
                          </Pointer>
                        </SummaryValue>
                      </LabelizedField>
                      <Dialog open={openDialog} onClose={handleClose}>
                        <DialogTitle>View IDs</DialogTitle>
                        <DialogContent>
                          <List>
                            {targetPopulation?.failedWalletValidationCollectorsIds?.map(
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
                      label={`Total Number of ${beneficiaryGroup?.groupLabelPlural}`}
                    >
                      <SummaryValue data-cy="total-number-of-households-count">
                        {targetPopulation.totalHouseholdsCount || '0'}
                      </SummaryValue>
                    </LabelizedField>
                  </SummaryBorder>
                </Grid>
                <Grid size={{ xs: 6 }}>
                  <SummaryBorder>
                    <LabelizedField
                      label={`Targeted ${beneficiaryGroup?.memberLabelPlural}`}
                    >
                      <SummaryValue>
                        {targetPopulation.totalIndividualsCount || '0'}
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
