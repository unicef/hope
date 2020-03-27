import React, { useState } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Typography, Paper, Button } from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';
import { Criteria } from './Criteria';
import { TargetCriteriaForm } from '../../containers/forms/TargetCriteriaForm';

const PaperContainer = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(5)}px;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(4)}px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ContentWrapper = styled.div`
  display: flex;
`;

const Divider = styled.div`
  border-left: 1px solid #b1b1b5;
  margin: 0 ${({ theme }) => theme.spacing(10)}px;
  position: relative;
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

interface TargetingCriteriaProps {
  criterias: object[];
  isEdit?: boolean;
  helpers?;
}

export function TargetingCriteria({
  criterias,
  isEdit = false,
  helpers,
}: TargetingCriteriaProps) {
  const { t } = useTranslation();
  const [isOpen, setOpen] = useState(false);
  const [criteriaObject, setCriteria] = useState({});
  const openModal = (criteria) => {
    setCriteria(criteria);
    setOpen(true);
  };
  const closeModal = () => {
    setCriteria({});
    setOpen(false);
  };

  const addCriteria = (values) => {
    //eslint-disable-next-line
    console.log('render', values);
    helpers.push(values.criterias);
    closeModal();
  };

  return (
    <div>
      <PaperContainer>
        <Title>
          <Typography variant='h6'>{t('Targeting Criteria')}</Typography>
          {isEdit && (
            <>
              {!!criterias.length && (
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
                title='Add targeting criteria'
                open={isOpen}
                onClose={() => closeModal()}
                addCriteria={addCriteria}
              />
            </>
          )}
        </Title>
        <ContentWrapper>
          {criterias.length ? (
            criterias.map((criteria, index) => {
              return (
                <>
                  <Criteria
                    isEdit={isEdit}
                    criteria={criteria}
                    editFunction={() => openModal(criteria)}
                    removeFunction={() => helpers.remove(index)}
                  />

                  {index % 2 ||
                  (criterias.length === 1 && index === 0) ? null : (
                    <Divider>
                      <DividerLabel>Or</DividerLabel>
                    </Divider>
                  )}
                </>
              );
            })
          ) : (
            <AddCriteria onClick={() => setOpen(true)}>
              <AddCircleOutline />
              <p>Add Criteria</p>
            </AddCriteria>
          )}
        </ContentWrapper>
      </PaperContainer>
    </div>
  );
}
