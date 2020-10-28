import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Typography, Paper } from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';

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
  flex-wrap: wrap;
  padding: ${({ theme }) => theme.spacing(4)}px 0;
`;

const IconWrapper = styled.div`
  display: flex;
  color: #a0b6d6;
`;

const AddCriteria = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  color: #003c8f;
  border: 2px solid #a0b6d6;
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

export function TargetingCriteriaDisabled(): React.ReactElement {
  const { t } = useTranslation();
  return (
    <div>
      <PaperContainer>
        <Title>
          <Typography variant='h6'>{t('Targeting Criteria')}</Typography>
        </Title>
        <ContentWrapper>
          <AddCriteria
            onClick={() => null}
            data-cy='button-target-population-disabled-add-criteria'
          >
            <IconWrapper>
              <AddCircleOutline />
              <p>Add Criteria</p>
            </IconWrapper>
          </AddCriteria>
        </ContentWrapper>
      </PaperContainer>
    </div>
  );
}
