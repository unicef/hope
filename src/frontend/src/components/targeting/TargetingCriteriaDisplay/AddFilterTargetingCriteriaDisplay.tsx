import { TargetingCriteriaForm } from '@containers/forms/TargetingCriteriaForm';
import {
  DataCollectingTypeType,
  PaymentPlanQuery,
  useAllCollectorFieldsAttributesQuery,
} from '@generated/graphql';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { AddCircleOutline } from '@mui/icons-material';
import { Box, Button } from '@mui/material';
import { Fragment, ReactElement, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { Criteria } from './Criteria';
import { ExcludeCheckboxes } from './ExcludeCheckboxes';
import {
  ContentWrapper,
  TargetingCriteriaDisplayDisabled,
} from './TargetingCriteriaDisplayDisabled';
import { VulnerabilityScoreComponent } from './VulnerabilityScoreComponent';
import { useCachedIndividualFieldsQuery } from '@hooks/useCachedIndividualFields';

const Title = styled.div`
  padding: ${({ theme }) => theme.spacing(3)} ${({ theme }) => theme.spacing(4)};
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Divider = styled.div`
  border-left: 1px solid #b1b1b5;
  margin: 0 ${({ theme }) => theme.spacing(10)};
  position: relative;
  transform: scale(0.9);
`;

const DividerLabel = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  color: #253b46;
  text-transform: uppercase;
  padding: 5px;
  border: 1px solid #b1b1b5;
  border-radius: 50%;
  background-color: #fff;
`;

const AddCriteria = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  color: #003c8f;
  border: 2px solid #033f91;
  border-radius: 3px;
  font-size: 16px;
  padding: ${({ theme }) => theme.spacing(6)}
    ${({ theme }) => theme.spacing(28)};
  cursor: pointer;
  p {
    font-weight: 500;
    margin: 0 0 0 ${({ theme }) => theme.spacing(2)};
  }
`;

interface AddFilterTargetingCriteriaDisplayProps {
  rules?;
  helpers?;
  targetPopulation?: PaymentPlanQuery['paymentPlan'];
  isEdit?: boolean;
  screenBeneficiary: boolean;
  isSocialDctType: boolean;
  isStandardDctType: boolean;
}

export const AddFilterTargetingCriteriaDisplay = ({
  rules,
  helpers,
  targetPopulation,
  isEdit,
  screenBeneficiary,
  isSocialDctType,
  isStandardDctType,
}: AddFilterTargetingCriteriaDisplayProps): ReactElement => {
  const { t } = useTranslation();
  const location = useLocation();
  const { selectedProgram } = useProgramContext();
  const { businessArea, programId } = useBaseUrl();

  const { data: allCoreFieldsAttributesData, loading } =
    useCachedIndividualFieldsQuery(businessArea, programId);
  const { data: allCollectorFieldsAttributesData } =
    useAllCollectorFieldsAttributesQuery({
      fetchPolicy: 'cache-first',
    });

  const [isOpen, setOpen] = useState(false);
  const [criteriaIndex, setIndex] = useState(0);
  const [criteriaObject, setCriteria] = useState({});
  const [allDataChoicesDict, setAllDataChoicesDict] = useState(null);
  const [allCollectorDataChoicesDict, setAllCollectorDataChoicesDict] =
    useState(null);

  useEffect(() => {
    if (loading) return;
    const allDataChoicesDictTmp =
      allCoreFieldsAttributesData?.allFieldsAttributes?.reduce((acc, item) => {
        acc[item.name] = item.choices;
        return acc;
      }, {});
    setAllDataChoicesDict(allDataChoicesDictTmp);
  }, [allCoreFieldsAttributesData, loading]);

  useEffect(() => {
    if (loading) return;
    const allCollectorDataChoicesDictTmp =
      allCollectorFieldsAttributesData?.allCollectorFieldsAttributes?.reduce(
        (acc, item) => {
          acc[item.name] = item.choices;
          return acc;
        },
        {},
      );
    setAllCollectorDataChoicesDict(allCollectorDataChoicesDictTmp);
  }, [allCollectorFieldsAttributesData, loading]);

  const regex = /(create|edit-tp)/;
  const isDetailsPage = !regex.test(location.pathname);

  const openModal = (criteria): void => {
    setCriteria(criteria);
    setOpen(true);
  };
  const closeModal = (): void => {
    setCriteria({});
    setIndex(null);
    return setOpen(false);
  };
  const editCriteria = (criteria, index): void => {
    setIndex(index);
    return openModal(criteria);
  };

  const addCriteria = (values): void => {
    const criteria = {
      householdsFiltersBlocks: [...values.householdsFiltersBlocks],
      individualsFiltersBlocks: [...values.individualsFiltersBlocks],
      collectorsFiltersBlocks: [...values.collectorsFiltersBlocks],
      householdIds: values.householdIds,
      individualIds: values.individualIds,
      deliveryMechanism: values.deliveryMechanism,
      fsp: values.fsp,
    };
    if (criteriaIndex !== null) {
      helpers.replace(criteriaIndex, criteria);
    } else {
      helpers.push(criteria);
    }
    return closeModal();
  };

  // const  collectorFiltersAvailable =
  //   selectedProgram?.dataCollectingType?.collectorFiltersAvailable;

  let individualFiltersAvailable =
    selectedProgram?.dataCollectingType?.individualFiltersAvailable;
  let householdFiltersAvailable =
    selectedProgram?.dataCollectingType?.householdFiltersAvailable;
  const isSocialWorkingProgram =
    selectedProgram?.dataCollectingType?.type === DataCollectingTypeType.Social;
  // Allow use filters on non-migrated programs
  if (individualFiltersAvailable === undefined) {
    individualFiltersAvailable = true;
  }
  if (householdFiltersAvailable === undefined) {
    householdFiltersAvailable = true;
  }

  // Disable household filters for social programs
  if (isSocialDctType) {
    householdFiltersAvailable = false;
  }

  if (householdFiltersAvailable || individualFiltersAvailable) {
    return (
      <Box display="flex" flexDirection="column">
        <Title>
          <div />
          {isEdit && (
            <>
              {!!rules.length && (
                <Button
                  variant="outlined"
                  color="primary"
                  onClick={() => setOpen(true)}
                  data-cy="button-target-population-add-criteria"
                >
                  {t('Add')} &apos;Or&apos; {t('Filter')}
                </Button>
              )}
            </>
          )}
        </Title>
        <TargetingCriteriaForm
          criteria={criteriaObject}
          open={isOpen}
          onClose={() => closeModal()}
          addCriteria={addCriteria}
          isSocialWorkingProgram={isSocialWorkingProgram}
          individualFiltersAvailable={individualFiltersAvailable}
          householdFiltersAvailable={householdFiltersAvailable}
          collectorsFiltersAvailable={true}
          targetPopulation={targetPopulation}
          criteriaIndex={criteriaIndex}
        />
        <ContentWrapper>
          <Box display="flex" flexDirection="column">
            <Box display="flex" flexWrap="wrap">
              {rules.length
                ? rules?.map((criteria, index) => (
                    // eslint-disable-next-line
                    <Fragment key={criteria.id || index}>
                      <Criteria
                        isEdit={isEdit}
                        allDataFieldsChoicesDict={allDataChoicesDict}
                        allCollectorFieldsChoicesDict={
                          allCollectorDataChoicesDict
                        }
                        canRemove={rules.length > 1}
                        rules={criteria.householdsFiltersBlocks || []}
                        individualsFiltersBlocks={
                          criteria.individualsFiltersBlocks || []
                        }
                        collectorsFiltersBlocks={
                          criteria.collectorsFiltersBlocks || []
                        }
                        householdIds={criteria.householdIds}
                        individualIds={criteria.individualIds}
                        editFunction={() => editCriteria(criteria, index)}
                        removeFunction={() => helpers.remove(index)}
                      />

                      {index === rules.length - 1 ||
                      (rules.length === 1 && index === 0) ? null : (
                        <Divider>
                          <DividerLabel>Or</DividerLabel>
                        </Divider>
                      )}
                    </Fragment>
                  ))
                : null}

              {!rules.length && (
                <AddCriteria
                  onClick={() => setOpen(true)}
                  data-cy="button-target-population-add-criteria"
                >
                  <AddCircleOutline />
                  <p>{t('Add Filter')}</p>
                </AddCriteria>
              )}
            </Box>
            <ExcludeCheckboxes
              isStandardDctType={isStandardDctType}
              isSocialDctType={isSocialDctType}
              screenBeneficiary={screenBeneficiary}
              isDetailsPage={isDetailsPage}
              targetPopulation={targetPopulation}
            />
          </Box>
        </ContentWrapper>
        {targetPopulation && (
          <VulnerabilityScoreComponent targetPopulation={targetPopulation} />
        )}
      </Box>
    );
  }
  return <TargetingCriteriaDisplayDisabled showTooltip />;
};
