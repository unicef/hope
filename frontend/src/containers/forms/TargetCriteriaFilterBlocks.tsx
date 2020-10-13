import styled from 'styled-components';
import { FieldArray } from 'formik';
import { Button } from '@material-ui/core';
import { AddCircleOutline } from '@material-ui/icons';
import React from 'react';
import { ImportedIndividualFieldsQuery } from '../../__generated__/graphql';
import { chooseFieldType, clearField } from '../../utils/targetingUtils';
import { TargetCriteriaBlockFilter } from './TargetCriteriaBlockFilter';

const Divider = styled.div`
  border-top: 1px solid #e2e2e2;
  margin: ${({ theme }) => theme.spacing(5)}px 0;
  position: relative;
`;
const DividerLabel = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 20px;
  height: 20px;
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
  text-align: center;
`;
const AndDivider = styled.div`
  border-top: 1px solid #b1b1b5;
  margin: ${({ theme }) => theme.spacing(10)}px 0;
  position: relative;
`;
const AndDividerLabel = styled.div`
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
const GrayFiltersBlock = styled.div`
  border: 1px solid #e0e0e0;
  border-radius: 3px;
`;
const AddIcon = styled(AddCircleOutline)`
  margin-right: 10px;
`;
const FilterWrapper = styled.div`
  padding-left: ${({ theme }) => theme.spacing(5)}px;
`;
export function TargetCriteriaFilterBlocks({
  blockIndex,
  data,
  values,
  onClick,
}: {
  blockIndex: number;
  data: ImportedIndividualFieldsQuery;
  values;
  onClick: () => void;
}): React.ReactElement {

  const shouldShowAndDivider =
    blockIndex + 1 < values.individualsFiltersBlocks.length;
  return (
    <div>
      Set Individual Criteria
      <FieldArray
        name={`individualsFiltersBlocks[${blockIndex}].individualBlockFilters`}
        render={(arrayHelpers) => (
          <div>
            <GrayFiltersBlock>
              {values.individualsFiltersBlocks[
                blockIndex
              ].individualBlockFilters.map((each, index) => {
                const shouldShowDivider =
                  index + 1 <
                  values.individualsFiltersBlocks[blockIndex]
                    .individualBlockFilters.length;
                return (
                  <>
                    <FilterWrapper>
                      <TargetCriteriaBlockFilter
                        blockIndex={blockIndex}
                        index={index}
                        data={data}
                        each={each}
                        onChange={(e, object) => {
                          if (object) {
                            return chooseFieldType(object, arrayHelpers, index);
                          }
                          return clearField(arrayHelpers, index);
                        }}
                        onClick={onClick}
                      />
                    </FilterWrapper>
                    {shouldShowDivider && (
                      <Divider>
                        <DividerLabel>+</DividerLabel>
                      </Divider>
                    )}
                  </>
                );
              })}
            </GrayFiltersBlock>
            <Button
              onClick={() =>
                arrayHelpers.push({
                  fieldName: '',
                })
              }
              color='primary'
            >
              <AddIcon />
              Add individual sub-criteria
            </Button>
          </div>
        )}
      />
      {shouldShowAndDivider && (
        <AndDivider>
          <AndDividerLabel>And</AndDividerLabel>
        </AndDivider>
      )}
    </div>
  );
}
