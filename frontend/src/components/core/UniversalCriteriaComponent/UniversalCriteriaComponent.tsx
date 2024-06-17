import { AddCircleOutline } from '@material-ui/icons';
import React, { Fragment, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { FieldAttributeNode } from '../../../__generated__/graphql';
import { addFieldAttributesToRules } from '../../../utils/targetingUtils';
import { useArrayToDict } from '../../../hooks/useArrayToDict';
import { UniversalCriteria } from './UniversalCriteria';
import { UniversalCriteriaForm } from './UniversalCriteriaForm';
import { UniversalCriteriaComponentDisabled } from './UniversalCriteriaComponentDisabled';

export const ContentWrapper = styled.div`
  display: flex;
  flex-wrap: wrap;
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

interface UniversalCriteriaProps {
  rules?;
  arrayHelpers?;
  individualDataNeeded?: boolean;
  isEdit?: boolean;
  individualFieldsChoices: FieldAttributeNode[];
  householdFieldsChoices: FieldAttributeNode[];
  isAddDialogOpen?: boolean;
  onAddDialogClose?: () => void;
  disabled?: boolean;
}

export const UniversalCriteriaComponent = ({
  rules,
  arrayHelpers,
  individualDataNeeded,
  isEdit,
  individualFieldsChoices,
  householdFieldsChoices,
  isAddDialogOpen,
  onAddDialogClose,
  disabled,
}: UniversalCriteriaProps): React.ReactElement => {
  const { t } = useTranslation();
  const [isOpen, setOpen] = useState(false);
  const [criteriaIndex, setIndex] = useState(null);
  const [criteriaObject, setCriteria] = useState({});

  const individualFieldsDict = useArrayToDict(
    individualFieldsChoices,
    'name',
    '*',
  );
  const householdFieldsDict = useArrayToDict(
    householdFieldsChoices,
    'name',
    '*',
  );
  const rulesWithFieldAttributes = useMemo(
    () =>
      addFieldAttributesToRules(
        rules,
        individualFieldsDict,
        householdFieldsDict,
      ),
    [rules, individualFieldsDict, householdFieldsDict],
  );
  useEffect(() => {
    if (isAddDialogOpen !== isOpen) {
      setOpen(isAddDialogOpen);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAddDialogOpen]);

  useEffect(() => {
    if (onAddDialogClose && !isOpen && isAddDialogOpen) {
      onAddDialogClose();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);
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
      arrayHelpers.replace(criteriaIndex, criteria);
    } else {
      arrayHelpers.push(criteria);
    }
    return closeModal();
  };

  const addCriteriaButton = disabled ? (
    <UniversalCriteriaComponentDisabled />
  ) : (
    <AddCriteria
      onClick={() => setOpen(true)}
      data-cy='button-universal-add-criteria'
    >
      <AddCircleOutline />
      <p>{t('Add Filter')}</p>
    </AddCriteria>
  );
  return (
    <>
      <UniversalCriteriaForm
        criteria={criteriaObject}
        open={isOpen}
        onClose={() => closeModal()}
        addCriteria={addCriteria}
        shouldShowWarningForIndividualFilter={individualDataNeeded}
        individualFieldsChoices={individualFieldsChoices}
        householdFieldsChoices={householdFieldsChoices}
      />
      <ContentWrapper>
        {rulesWithFieldAttributes.length
          ? rulesWithFieldAttributes.map((criteria, index) => {
              return (
                //eslint-disable-next-line
                <Fragment key={criteria.id || index}>
                  <UniversalCriteria
                    isEdit={isEdit}
                    canRemove={rulesWithFieldAttributes.length > 1}
                    rules={criteria.filters}
                    individualsFiltersBlocks={
                      criteria.individualsFiltersBlocks || []
                    }
                    editFunction={() => editCriteria(criteria, index)}
                    removeFunction={() => arrayHelpers.remove(index)}
                  />

                  {index === rulesWithFieldAttributes.length - 1 ||
                  (rulesWithFieldAttributes.length === 1 &&
                    index === 0) ? null : (
                    <Divider>
                      <DividerLabel>Or</DividerLabel>
                    </Divider>
                  )}
                </Fragment>
              );
            })
          : addCriteriaButton}
      </ContentWrapper>
    </>
  );
};
