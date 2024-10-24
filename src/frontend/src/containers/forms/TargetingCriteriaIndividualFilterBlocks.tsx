import { Box, Button } from '@mui/material';
import { AddCircleOutline } from '@mui/icons-material';
import { FieldArray } from 'formik';
import { Fragment } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { chooseFieldType, clearField } from '@utils/targetingUtils';
import { ImportedIndividualFieldsQuery } from '@generated/graphql';
import { TargetingCriteriaIndividualBlockFilter } from './TargetingCriteriaIndividualBlockFilter';

const Divider = styled.div`
  border-top: 1px solid #e2e2e2;
  margin: ${({ theme }) => theme.spacing(5)} 0;
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
  margin: ${({ theme }) => theme.spacing(10)} 0;
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
  margin-bottom: 20px;
  padding-top: 20px;
`;

const FilterWrapper = styled.div`
  padding: ${({ theme }) => theme.spacing(3)} ${({ theme }) => theme.spacing(5)};
`;
export function TargetingCriteriaIndividualFilterBlocks({
  blockIndex,
  data,
  values,
  choicesToDict,
  onDelete,
}: {
  blockIndex: number;
  data: ImportedIndividualFieldsQuery;
  values;
  choicesToDict;
  onDelete: () => void;
}): React.ReactElement {
  const { t } = useTranslation();
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
                  <Fragment key={blockIndex + index.toString()}>
                    <FilterWrapper>
                      <TargetingCriteriaIndividualBlockFilter
                        blockIndex={blockIndex}
                        index={index}
                        data={data}
                        each={each}
                        choicesDict={choicesToDict}
                        onChange={(e, object) => {
                          if (object) {
                            return chooseFieldType(object, arrayHelpers, index);
                          }
                          return clearField(arrayHelpers, index);
                        }}
                        onDelete={() => {
                          if (
                            values.individualsFiltersBlocks[blockIndex]
                              .individualBlockFilters.length === 1
                          ) {
                            onDelete();
                            return;
                          }
                          arrayHelpers.remove(index);
                        }}
                      />
                    </FilterWrapper>
                    {shouldShowDivider && (
                      <Divider>
                        <DividerLabel>+</DividerLabel>
                      </Divider>
                    )}
                  </Fragment>
                );
              })}
              <Box display="flex" justifyContent="center">
                <Button
                  color="primary"
                  variant="outlined"
                  startIcon={<AddCircleOutline />}
                  onClick={() =>
                    arrayHelpers.push({
                      fieldName: '',
                    })
                  }
                  style={{
                    position: 'relative',
                    top: 18,
                    backgroundColor: '#fff',
                  }}
                >
                  {t('Add Next Rule')}
                </Button>
              </Box>
            </GrayFiltersBlock>
          </div>
        )}
      />
      {shouldShowAndDivider && (
        <AndDivider>
          <AndDividerLabel>{t('And')}</AndDividerLabel>
        </AndDivider>
      )}
    </div>
  );
}
