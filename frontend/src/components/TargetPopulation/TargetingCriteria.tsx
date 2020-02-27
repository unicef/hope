import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { Typography, Paper } from '@material-ui/core';

const data = [
  {
    intakeGroup: 'Children 9/10/2019',
    sex: 'Female',
    age: '7 - 15 years old',
    distanceToSchool: 'over 3km',
    household: 'over 5 individuals',
  },
  {
    intakeGroup: 'Children 9/10/2019',
    sex: 'Male',
    age: null,
    distanceToSchool: 'over 3km',
    household: null,
  },
];

const PaperContainer = styled(Paper)`
  padding: ${({ theme }) => theme.spacing(3)}px
    ${({ theme }) => theme.spacing(4)}px;
  margin: ${({ theme }) => theme.spacing(5)}px;
  border-bottom: 1px solid rgba(224, 224, 224, 1);
`;

const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(2)}px;
`;

const ContentWrapper = styled.div`
  display: flex;
`;

const Criteria = styled.div`
  width: 380px;
  border: 2px solid #033f91;
  border-radius: 3px;
  font-size: 16px;
  background-color: #f7faff;
  padding: ${({ theme }) => theme.spacing(3)}px;
  p {
    margin: ${({ theme }) => theme.spacing(2)}px 0;
    span {
      color: #003c8f;
    }
  }
`;
//eslint-disable-next-line
export function TargetingCriteria() {
  const { t } = useTranslation();

  return (
    <div>
      <PaperContainer>
        <Title>
          <Typography variant='h6'>{t('Targeting Criteria')}</Typography>
        </Title>
        <ContentWrapper>
          {data.map((criteria) => {
            return (
              <Criteria>
                {criteria.intakeGroup && (
                  <p>
                    Intake group: <span>{criteria.intakeGroup}</span>
                  </p>
                )}
                {criteria.sex && (
                  <p>
                    Sex: <span>{criteria.sex}</span>
                  </p>
                )}
                {criteria.age && (
                  <p>
                    Age: <span>{criteria.age}</span>
                  </p>
                )}
                {criteria.distanceToSchool && (
                  <p>
                    Distance to school: <span>{criteria.distanceToSchool}</span>
                  </p>
                )}
                {criteria.household && (
                  <p>
                    Hoousehold size: <span>{criteria.household}</span>
                  </p>
                )}
              </Criteria>
            );
          })}
          
        </ContentWrapper>
        {/* <Criteria>Add Criteria</Criteria> */}
      </PaperContainer>
    </div>
  );
}
