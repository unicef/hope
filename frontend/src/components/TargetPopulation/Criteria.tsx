import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { IconButton } from '@material-ui/core';
import { Delete, Edit } from '@material-ui/icons';

const CriteriaElement = styled.div`
  width: 380px;
  position: relative;
  border: 2px solid #033f91;
  border-radius: 3px;
  font-size: 16px;
  background-color: #f7faff;
  padding: ${({ theme }) => theme.spacing(1)}px
    ${({ theme }) => theme.spacing(3)}px;
  p {
    margin: ${({ theme }) => theme.spacing(2)}px 0;
    span {
      color: #003c8f;
      font-weight: bold;
    }
  }
`;

const ButtonsContainer = styled.div`
  position: absolute;
  right: 0;
  top: 0;
  button {
    color: #949494;
    padding: 12px 8px;
    svg {
      width: 20px;
      height: 20px;
    }
  }
`;

const CriteriaField = ({field}) => {
  let fieldElement;
  switch (field.comparisionMethod) {
    case 'NOT_EQUALS':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}: <span>{field.arguments[0]}</span>
        </p>
      )
      break;
    case 'RANGE':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}:{' '}
          <span>
            {field.arguments[0]} - {field.arguments[1]}
          </span>
        </p>
      )
      break;
    case 'EQUALS':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}: <span>{field.arguments[0]}</span>
        </p>
      )
      break;
    case 'LESS_THAN':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}: {'>'} <span>{field.arguments[0]}</span>
        </p>
      )
      break;
    case 'GREATER_THAN':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}: {'<'} <span>{field.arguments[0]}</span>
        </p>
      )
      break;
    default:
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn}: <span>{field.arguments[0]}</span>
        </p>
      )
      break;
  }
  return fieldElement;
};

export function Criteria({ rules, removeFunction, editFunction, isEdit }) {
  const { t } = useTranslation();
  return (
    <CriteriaElement>
      {rules.map((each) => (
        <CriteriaField key={each.id} field={each} />
      ))}
      {isEdit && (
        <ButtonsContainer>
          <IconButton>
            <Edit onClick={editFunction} />
          </IconButton>
          <IconButton onClick={removeFunction}>
            <Delete />
          </IconButton>
        </ButtonsContainer>
      )}
    </CriteriaElement>
  );
}
