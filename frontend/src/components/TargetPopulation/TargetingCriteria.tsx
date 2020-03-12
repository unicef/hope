import React, { useState } from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Typography, Paper, Button } from '@material-ui/core';
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
  font-size: 14px;
  font-weight: 500;
  color: #253b46;
  text-transform: uppercase;
  padding: 5px;
  border: 1px solid #b1b1b5;
  border-radius: 50%;
  background-color: #fff;
`;

interface TargetingCriteriaProps {
  criterias: object[];
  isEdit: boolean;
  helpers?;
}

export function TargetingCriteria({
  criterias,
  isEdit,
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

  return (
    <div>
      <PaperContainer>
        <Title>
          <Typography variant='h6'>{t('Targeting Criteria')}</Typography>
          {isEdit && (
            <>
              <Button
                variant='contained'
                color='primary'
                onClick={() => setOpen(true)}
              >
                Add Criteria
              </Button>
              <TargetCriteriaForm
                criteria={criteriaObject}
                title='Add targeting criteria'
                open={isOpen}
                onClose={() => closeModal()}
              />
            </>
          )}
        </Title>
        <ContentWrapper>
          {criterias.map((criteria, index) => {
            return (
              <>
                <Criteria
                  isEdit={isEdit}
                  criteria={criteria}
                  editFunction={() => openModal(criteria)}
                  removeFunction={() => helpers.remove(index)}
                />

                {index % 2 ? null : (
                  <Divider>
                    <DividerLabel>Or</DividerLabel>
                  </Divider>
                )}
              </>
            );
          })}
        </ContentWrapper>
      </PaperContainer>
    </div>
  );
}
