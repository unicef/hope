import { IconButton } from '@mui/material';
import { Delete, Edit } from '@mui/icons-material';
import * as React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import GreaterThanEqual from '../../../assets/GreaterThanEqual.svg';
import LessThanEqual from '../../../assets/LessThanEqual.svg';
import { TargetingCriteriaRuleObjectType } from '@generated/graphql';
import { Box } from '@mui/system';

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

const PduDataBox = styled(Box)`
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 3px;
  padding: ${({ theme }) => theme.spacing(3)};
  margin: ${({ theme }) => theme.spacing(3)};
`;

const CriteriaField = ({ field, choicesDict }): React.ReactElement => {
  const extractChoiceLabel = (choiceField, argument) => {
    let choices = choicesDict?.[choiceField.fieldName];
    if (!choices) {
      choices = choiceField.fieldAttribute.choices;
    }
    return choices?.length
      ? choices.find((each) => each.value === argument)?.labelEn
      : argument;
  };

  const displayValueOrEmpty = (value) => (value ? value : 'Empty');

  const { t } = useTranslation();
  let fieldElement;

  switch (field.comparisonMethod) {
    case 'NOT_EQUALS':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}:{' '}
          <span>{displayValueOrEmpty(field.arguments?.[0])}</span>
        </p>
      );
      break;
    case 'RANGE':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}:{' '}
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
          {field.fieldAttribute.labelEn || field.fieldName}:{' '}
          {field.fieldAttribute.type === 'BOOL' ||
          field.fieldAttribute?.pduData?.subtype ? (
            field.isNull ? (
              <span>{t('Empty')}</span>
            ) : (
              <span>{field.arguments?.[0] ? t('Yes') : t('No')}</span>
            )
          ) : (
            <span>
              {field.arguments?.[0] != null ? field.arguments[0] : t('Empty')}
            </span>
          )}
        </p>
      );
      break;
    case 'LESS_THAN':
    case 'GREATER_THAN': {
      const isLessThan = field.type === 'LESS_THAN';
      const MathSignComponent = isLessThan ? LessThanEqual : GreaterThanEqual;
      const altText = isLessThan ? 'less_than' : 'greater_than';
      const displayValue = field.arguments?.[0];

      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}:{' '}
          {displayValue && <MathSign src={MathSignComponent} alt={altText} />}
          <span>{displayValueOrEmpty(displayValue)}</span>
        </p>
      );
      break;
    }
    case 'CONTAINS':
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn || field.fieldName}:{' '}
          {field.arguments?.map((argument, index) => (
            <React.Fragment key={index}>
              <span>
                {displayValueOrEmpty(extractChoiceLabel(field, argument))}
              </span>
              {index !== field.arguments.length - 1 && ', '}
            </React.Fragment>
          ))}
        </p>
      );
      break;
    default:
      fieldElement = (
        <p>
          {field.fieldAttribute.labelEn}:{' '}
          <span>{displayValueOrEmpty(field.arguments?.[0])}</span>
        </p>
      );
      break;
  }

  return (
    <>
      {fieldElement}
      {field.type === 'PDU' &&
        field.pduData &&
        field.round &&
        field.pduData.roundsNames?.[field.round - 1] && (
          <PduDataBox>
            {field.round}-{field.pduData.roundsNames[field.round - 1]}
          </PduDataBox>
        )}
    </>
  );
};

interface CriteriaProps {
  rules: [TargetingCriteriaRuleObjectType];
  individualsFiltersBlocks;
  removeFunction?;
  editFunction?;
  isEdit: boolean;
  canRemove: boolean;
  alternative?: boolean;
  choicesDict;
}

export function Criteria({
  rules,
  removeFunction = () => null,
  editFunction = () => null,
  isEdit,
  canRemove,
  choicesDict,
  alternative = null,
  individualsFiltersBlocks,
}: CriteriaProps): React.ReactElement {
  return (
    <CriteriaElement alternative={alternative} data-cy="criteria-container">
      {(rules || []).map((each, index) => (
        <CriteriaField choicesDict={choicesDict} key={index} field={each} />
      ))}
      {individualsFiltersBlocks.map((item, index) => (
        <CriteriaSetBox key={index}>
          {item.individualBlockFilters.map((filter, filterIndex) => (
            <CriteriaField
              choicesDict={choicesDict}
              key={filterIndex}
              field={filter}
            />
          ))}
        </CriteriaSetBox>
      ))}
      {isEdit && (
        <ButtonsContainer>
          <IconButton data-cy="button-edit" onClick={editFunction}>
            <Edit />
          </IconButton>
          {canRemove && (
            <IconButton data-cy="button-remove" onClick={removeFunction}>
              <Delete />
            </IconButton>
          )}
        </ButtonsContainer>
      )}
    </CriteriaElement>
  );
}
