import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';

const CriteriaElement = styled.div`
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
      font-weight: bold;
    }
  }
`;

export function Criteria({ criteria }) {
  const { t } = useTranslation();

  return (
    <CriteriaElement>
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
    </CriteriaElement>
  );
}
