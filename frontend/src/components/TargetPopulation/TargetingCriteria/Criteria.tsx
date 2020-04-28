import React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';
import { IconButton } from '@material-ui/core';
import { Delete, Edit } from '@material-ui/icons';
import { TargetingCriteriaRuleObjectType } from '../../../__generated__/graphql';

const CriteriaElement = styled.div`
  width: ${(props) => (props.alternative ? 'auto' : '380px')};
  position: relative;
  border: ${(props) => (props.alternative ? '0' : '2px solid #033f91')};
  border-radius: 3px;
  font-size: 16px;
  background-color: ${(props) =>
    props.alternative ? 'transparent' : '#f7faff'};
  padding: ${({ theme }) => theme.spacing(1)}px
    ${({ theme }) => theme.spacing(3)}px;
  margin: ${({ theme }) => theme.spacing(2)}px 0;
  p {
    margin: ${({ theme }) => theme.spacing(2)}px 0;
    span {
      color: ${(props) => (props.alternative ? '#000' : '#003c8f')};
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

const CriteriaField = ({ field }) => {
  let fieldElement;
  switch (field.comparisionMethod) {
    case 'NOT_EQUALS':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}:{' '}
          <span>{field.arguments[0]}</span>
        </p>
      );
      break;
    case 'RANGE':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}:{' '}
          <span>
            {field.arguments[0]} - {field.arguments[1]}
          </span>
        </p>
      );
      break;
    case 'EQUALS':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}:{' '}
          <span>{field.arguments[0]}</span>
        </p>
      );
      break;
    case 'LESS_THAN':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}: {'<'}{' '}
          <span>{field.arguments[0]}</span>
        </p>
      );
      break;
    case 'GREATER_THAN':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}: {'>'}{' '}
          <span>{field.arguments[0]}</span>
        </p>
      );
      break;
    default:
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn}: <span>{field.arguments[0]}</span>
        </p>
      );
      break;
  }
  return fieldElement;
};

interface CriteriaProps {
  rules: [TargetingCriteriaRuleObjectType];
  removeFunction?;
  editFunction?;
  isEdit: boolean;
  canRemove: boolean;
  alternative?: boolean;
}

export function Criteria({
  rules,
  removeFunction,
  editFunction,
  isEdit,
  canRemove,
  alternative,
}: CriteriaProps) {
  const { t } = useTranslation();
  return (
    <CriteriaElement alternative={alternative}>
      {rules.map((each, index) => {
        //eslint-disable-next-line
        return <CriteriaField key={index} field={each} />;
      })}
      {isEdit && (
        <ButtonsContainer>
          <IconButton>
            <Edit onClick={editFunction} />
          </IconButton>
          {canRemove && (
            <IconButton onClick={removeFunction}>
              <Delete />
            </IconButton>
          )}
        </ButtonsContainer>
      )}
    </CriteriaElement>
  );
}
