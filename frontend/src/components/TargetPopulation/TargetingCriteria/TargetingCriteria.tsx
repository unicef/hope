import React, { useState } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import {
  Typography,
  Paper,
  Button,
  Select,
  FormControl,
  MenuItem,
  InputLabel,
  TextField,
  Box,
} from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';
import { TargetCriteriaForm } from '../../../containers/forms/TargetCriteriaForm';
import { Criteria } from './Criteria';
import {
  AllProgramsQuery,
  TargetPopulationQuery,
  useAllSteficonRulesQuery,
  useSetSteficonRuleOnTargetPopulationMutation,
  useUpdateTpMutation,
} from '../../../__generated__/graphql';
import { CashPlan } from '../../../apollo/queries/CashPlan';
import { TARGET_POPULATION_QUERY } from '../../../apollo/queries/TargetPopulation';

const PaperContainer = styled(Paper)`
  margin: ${({ theme }) => theme.spacing(5)}px;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

const Title = styled.div`
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ContentWrapper = styled.div`
  display: flex;
  flex-wrap: wrap;
  padding: ${({ theme }) => theme.spacing(4)}px
    ${({ theme }) => theme.spacing(4)}px;
`;

const Divider = styled.div`
  border-left: 1px solid #b1b1b5;
  margin: 0 ${({ theme }) => theme.spacing(10)}px;
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

const VulnerabilityScoreDivider = styled.div`
  width: 100%;
  height: 1px;
  background-color: #e0e0e0;
`;
const SelectRow = styled.div`
  display: flex;
  flex-direction: row;
  width: 100%;
  align-items: center;
`;
const CriteriaElement = styled.div`
  width: auto;
  max-width: 380px;
  position: relative;
  border: ${(props) => (props.alternative ? '0' : '2px solid #033f91')};
  border-radius: 3px;
  font-size: 16px;
  background-color: ${(props) =>
    props.alternative ? 'transparent' : '#f7faff'};
  padding: ${({ theme }) => theme.spacing(1)}px
    ${({ theme, alternative }) =>
      alternative ? theme.spacing(1) : theme.spacing(17)}px
    ${({ theme }) => theme.spacing(1)}px ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(2)}px 0;
  p {
    margin: ${({ theme }) => theme.spacing(2)}px 0;
    span {
      color: ${(props) => (props.alternative ? '#000' : '#003c8f')};
      font-weight: bold;
    }
  }
`;

const ButtonMargin = styled(Button)`
  && {
    margin-top: 4px;
    margin-left: ${({ theme }) => theme.spacing(4)}px;
    height: 40px;
  }
`;

const AddCriteria = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  color: #003c8f;
  border: 2px solid #033f91;
  border-radius: 3px;
  font-size: 16px;
  padding: ${({ theme }) => theme.spacing(6)}px
    ${({ theme }) => theme.spacing(28)}px;
  cursor: pointer;
  p {
    font-weight: 500;
    margin: 0 0 0 ${({ theme }) => theme.spacing(2)}px;
  }
`;
const StyledTextField = styled(TextField)`
  input[type='number']::-webkit-inner-spin-button,
  input[type='number']::-webkit-outer-spin-button {
    -webkit-appearance: none;
  }
  input[type='number'] {
    -moz-appearance: textfield;
  }
  && {
    margin: 0 ${({ theme }) => theme.spacing(2)}px;
  }
`;

const ApplyScoreRange = styled.div`
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  margin: ${({ theme }) => theme.spacing(2)}px;
`;

interface TargetingCriteriaProps {
  candidateListRules?;
  targetPopulationRules?;
  isEdit?: boolean;
  helpers?;
  selectedProgram?: AllProgramsQuery['allPrograms']['edges'][number]['node'];
  targetPopulation?: TargetPopulationQuery['targetPopulation'];
}

function VulnerabilityScoreComponent({
  targetPopulation,
}: {
  targetPopulation: TargetPopulationQuery['targetPopulation'];
}): React.ReactElement {
  const [setSteficonRule] = useSetSteficonRuleOnTargetPopulationMutation({
    refetchQueries: () => [
      {
        query: TARGET_POPULATION_QUERY,
        variables: {
          id: targetPopulation?.id,
        },
      },
    ],
  });
  const [updateTargetPopulation] = useUpdateTpMutation({
    refetchQueries: () => [
      {
        query: TARGET_POPULATION_QUERY,
        variables: {
          id: targetPopulation?.id,
        },
      },
    ],
  });
  const [vulnerabilityScoreMinValue, setVulnerabilityScoreMinValue] = useState(
    targetPopulation?.vulnerabilityScoreMin,
  );
  const [vulnerabilityScoreMaxValue, setVulnerabilityScoreMaxValue] = useState(
    targetPopulation?.vulnerabilityScoreMax,
  );
  const [steficonRuleValue, setSteficonRuleValue] = useState(
    targetPopulation?.steficonRule?.id,
  );
  const { data, loading } = useAllSteficonRulesQuery();
  if (targetPopulation?.status !== 'APPROVED') {
    return null;
  }
  let menuItems = [];
  if (!loading) {
    menuItems = data.allSteficonRules.edges.map((item) => {
      return (
        <MenuItem key={item.node.id} value={item.node.id}>
          {item.node.name}
        </MenuItem>
      );
    });
    menuItems.splice(
      0,
      0,
      <MenuItem key='-1' value={null}>
        None
      </MenuItem>,
    );
  }
  let criteriaBox = null;
  if (targetPopulation?.steficonRule?.id) {
    criteriaBox = (
      <CriteriaElement>
        <p>Vulnerability score:</p>
        <Box
          display='flex'
          flexDirection='row'
          alignItems='center'
          justifyContent='center'
        >
          From{' '}
          <StyledTextField
            variant='outlined'
            value={vulnerabilityScoreMinValue}
            margin='dense'
            label='From'
            onChange={(event) =>
              setVulnerabilityScoreMinValue(event.target.value)
            }
          />{' '}
          To{' '}
          <StyledTextField
            variant='outlined'
            value={vulnerabilityScoreMaxValue}
            margin='dense'
            label='To'
            onChange={(event) =>
              setVulnerabilityScoreMaxValue(event.target.value)
            }
          />
        </Box>
        <ApplyScoreRange>
          <Button
            variant='contained'
            color='primary'
            disabled={
              vulnerabilityScoreMinValue ===
                targetPopulation?.vulnerabilityScoreMin &&
              vulnerabilityScoreMaxValue ===
                targetPopulation?.vulnerabilityScoreMax
            }
            onClick={() =>
              updateTargetPopulation({
                variables: {
                  input: {
                    id: targetPopulation.id,
                    vulnerabilityScoreMin: vulnerabilityScoreMinValue,
                    vulnerabilityScoreMax: vulnerabilityScoreMaxValue,
                  },
                },
              })
            }
          >
            Apply
          </Button>
        </ApplyScoreRange>
      </CriteriaElement>
    );
  }
  return (
    <>
      <VulnerabilityScoreDivider />
      <ContentWrapper>
        <SelectRow>
          <FormControl variant='outlined' margin='dense' fullWidth>
            <InputLabel>Apply Additional Formula</InputLabel>
            <Select
              value={steficonRuleValue}
              labelWidth={180}
              onChange={(event) =>
                setSteficonRuleValue(event.target.value as string)
              }
            >
              {menuItems}
            </Select>
          </FormControl>
          <ButtonMargin
            variant='contained'
            color='primary'
            onClick={() =>
              setSteficonRule({
                variables: {
                  input: {
                    targetId: targetPopulation.id,
                    steficonRuleId: steficonRuleValue,
                  },
                },
              })
            }
            disabled={targetPopulation?.steficonRule?.id === steficonRuleValue}
          >
            Apply
          </ButtonMargin>
        </SelectRow>
        {criteriaBox}
      </ContentWrapper>
    </>
  );
}

export function TargetingCriteria({
  candidateListRules,
  targetPopulationRules = [],
  isEdit = false,
  helpers,
  selectedProgram,
  targetPopulation,
}: TargetingCriteriaProps): React.ReactElement {
  const { t } = useTranslation();
  const [isOpen, setOpen] = useState(false);
  const [criteriaIndex, setIndex] = useState(null);
  const [criteriaObject, setCriteria] = useState({});
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
      filters: [...values.filters],
      individualsFiltersBlocks: [...values.individualsFiltersBlocks],
    };
    if (criteriaIndex !== null) {
      helpers.replace(criteriaIndex, criteria);
    } else {
      helpers.push(criteria);
    }
    return closeModal();
  };
  return (
    <div>
      <PaperContainer>
        <Title>
          <Typography variant='h6'>{t('Targeting Criteria')}</Typography>
          {isEdit && (
            <>
              {!!candidateListRules.length && (
                <Button
                  variant='contained'
                  color='primary'
                  onClick={() => setOpen(true)}
                >
                  Add Criteria
                </Button>
              )}
              <TargetCriteriaForm
                criteria={criteriaObject}
                title='Add Filter'
                open={isOpen}
                onClose={() => closeModal()}
                addCriteria={addCriteria}
              />
            </>
          )}
        </Title>
        <ContentWrapper>
          {candidateListRules.length ? (
            candidateListRules.map((criteria, index) => {
              return (
                <>
                  <Criteria
                    //eslint-disable-next-line
                    key={criteria.id || index}
                    isEdit={isEdit}
                    canRemove={candidateListRules.length > 1}
                    rules={criteria.filters}
                    individualsFiltersBlocks={
                      criteria.individualsFiltersBlocks || []
                    }
                    editFunction={() => editCriteria(criteria, index)}
                    removeFunction={() => helpers.remove(index)}
                  />

                  {index === candidateListRules.length - 1 ||
                  (candidateListRules.length === 1 && index === 0) ? null : (
                    <Divider>
                      <DividerLabel>Or</DividerLabel>
                    </Divider>
                  )}
                </>
              );
            })
          ) : (
            <AddCriteria
              onClick={() => setOpen(true)}
              data-cy='button-target-population-add-criteria'
            >
              <AddCircleOutline />
              <p>Add Criteria</p>
            </AddCriteria>
          )}
        </ContentWrapper>
        <VulnerabilityScoreComponent targetPopulation={targetPopulation} />
      </PaperContainer>
    </div>
  );
}
