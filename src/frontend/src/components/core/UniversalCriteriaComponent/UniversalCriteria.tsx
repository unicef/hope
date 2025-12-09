import React, { ReactElement } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import GreaterThanEqual from '../../../assets/GreaterThanEqual.svg';
import LessThanEqual from '../../../assets/LessThanEqual.svg';
import { Fragment } from 'react/jsx-runtime';
import { fieldNameToLabel } from '@utils/utils';
import { Edit, Delete } from '@mui/icons-material';
import { IconButton } from '@mui/material';

interface CriteriaElementProps {
  alternative?: boolean;
}

const CriteriaElement = styled.div<CriteriaElementProps>`
  width: auto;
  max-width: 380px;
  position: relative;
  border: ${(props) => (props.alternative ? '0' : '2px solid #033f91')};
  border-radius: 3px;
  font-size: 16px;
  background-color: ${(props) =>
    props.alternative ? 'transparent' : '#f7faff'};
  padding: ${({ theme }) => theme.spacing(1)}
    ${({ theme, alternative }) =>
      alternative ? theme.spacing(1) : theme.spacing(17)}
    ${({ theme }) => theme.spacing(1)} ${({ theme }) => theme.spacing(4)};
  margin: ${({ theme }) => theme.spacing(2)} 0;
  p {
    margin: ${({ theme }) => theme.spacing(2)} 0;
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

const MathSign = styled.img`
  width: 20px;
  height: 20px;
  vertical-align: middle;
`;

const CriteriaSetBox = styled.div`
  border: 1px solid #607cab;
  border-radius: 3px;
  padding: 0 ${({ theme }) => theme.spacing(2)};
  margin: ${({ theme }) => theme.spacing(2)} 0;
`;

function getFieldLabel(field) {
  if (field.fieldAttribute?.labelEn) {
    if (typeof field.fieldAttribute.labelEn === 'string')
      return field.fieldAttribute.labelEn;
    if (
      field.fieldAttribute.labelEn &&
      typeof field.fieldAttribute.labelEn.englishEn === 'string'
    )
      return field.fieldAttribute.labelEn.englishEn;
  }
  const labelEn = field.labelEn;
  if (typeof labelEn === 'string') return labelEn;
  if (labelEn && typeof labelEn.englishEn === 'string')
    return labelEn.englishEn;
  return fieldNameToLabel(field.fieldName);
}

const CriteriaField = ({ field }): ReactElement => {
  const { t } = useTranslation();

  const extractChoiceLabel = (choiceField, argument) => {
    const choices =
      choiceField?.choices || choiceField?.fieldAttribute?.choices;
    return choices?.length
      ? choices.find((each) => each.value === argument)?.labelEn
      : argument;
  };

  const displayValueOrEmpty = (value) => (value ? value : 'Empty');

  let fieldElement;
  switch (field.comparisonMethod) {
    case 'NOT_EQUALS':
      fieldElement = (
        <p>
          {getFieldLabel(field)}:{' '}
          <span>{displayValueOrEmpty(field.arguments?.[0])}</span>
        </p>
      );
      break;
    case 'RANGE':
      fieldElement = (
        <p>
          {getFieldLabel(field)}:{' '}
          <span>
            {displayValueOrEmpty(field.arguments?.[0])} -{' '}
            {displayValueOrEmpty(field.arguments?.[1])}
          </span>
        </p>
      );
      break;
    case 'EQUALS':
      fieldElement = (
        <p>
          {getFieldLabel(field)}:{' '}
          {field.isNull === true || field.comparisonMethod === 'IS_NULL' ? (
            <span>{t('Empty')}</span>
          ) : typeof field.arguments?.[0] === 'boolean' ? (
            field.arguments[0] ? (
              <span>{t('Yes')}</span>
            ) : (
              <span>{t('No')}</span>
            )
          ) : (
            <>
              {field.arguments?.[0] != null ? (
                field.arguments[0] === 'Yes' ? (
                  <span>{t('Yes')}</span>
                ) : field.arguments[0] === 'No' ? (
                  <span>{t('No')}</span>
                ) : (
                  <span>{extractChoiceLabel(field, field.arguments[0])}</span>
                )
              ) : (
                <span>{t('Empty')}</span>
              )}
            </>
          )}
        </p>
      );
      break;
    case 'LESS_THAN':
    case 'GREATER_THAN': {
      const isLessThan = field?.comparisonMethod === 'LESS_THAN';
      const MathSignComponent = isLessThan ? LessThanEqual : GreaterThanEqual;
      const altText = isLessThan ? 'less_than' : 'greater_than';
      const displayValue = field.arguments?.[0];

      fieldElement = (
        <p>
          {getFieldLabel(field)}:{' '}
          {displayValue && <MathSign src={MathSignComponent} alt={altText} />}
          <span>{displayValueOrEmpty(displayValue)}</span>
        </p>
      );
      break;
    }
    case 'CONTAINS':
      fieldElement = (
        <p>
          {getFieldLabel(field)}:{' '}
          {field.arguments?.map((argument, index) => (
            <Fragment key={index}>
              <span>
                {displayValueOrEmpty(extractChoiceLabel(field, argument))}
              </span>
              {index !== field.arguments.length - 1 && ', '}
            </Fragment>
          ))}
        </p>
      );
      break;
    default:
      fieldElement = (
        <p>
          {getFieldLabel(field)}:{' '}
          <span>{displayValueOrEmpty(field.arguments?.[0])}</span>
        </p>
      );
      break;
  }
  return fieldElement;
};

interface CriteriaProps {
  rules: [any];
  individualsFiltersBlocks;
  removeFunction?;
  editFunction?;
  isEdit: boolean;
  canRemove: boolean;
  alternative?: boolean;
}

export function UniversalCriteria({
  rules,
  removeFunction = () => null,
  editFunction = () => null,
  isEdit,
  canRemove,
  alternative = null,
  individualsFiltersBlocks,
}: CriteriaProps): ReactElement {
  return (
    <CriteriaElement alternative={alternative} data-cy="criteria-container">
      {(rules || []).map((each, index) => (
        <CriteriaField key={index} field={each} />
      ))}
      {individualsFiltersBlocks.map(
        (item, index) =>
          item.individualBlockFilters.length > 0 && (
            <CriteriaSetBox key={index}>
              {item.individualBlockFilters.map((filter, filterIndex) => (
                <CriteriaField key={filterIndex} field={filter} />
              ))}
            </CriteriaSetBox>
          ),
      )}
      {isEdit && (
        <ButtonsContainer>
          <IconButton onClick={editFunction}>
            <Edit />
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
