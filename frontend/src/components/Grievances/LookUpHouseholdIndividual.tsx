import React, { useState } from 'react';
import SearchIcon from '@material-ui/icons/Search';
import styled from 'styled-components';
import { LookUpHouseholdIndividualDisplay } from './LookUpHouseholdIndividualDisplay';
import { LookUpHouseholdIndividualModal } from './LookUpHouseholdIndividualModal';

const LookUp = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1.5px solid #043e91;
  border-radius: 5px;
  color: #033f91;
  font-size: 16px;
  text-align: center;
  padding: 25px;
  font-weight: 500;
  cursor: pointer;
`;
const MarginRightSpan = styled.span`
  margin-right: 5px;
`;
export const LookUpHouseholdIndividual = ({
  onValueChange,
  values,
}): React.ReactElement => {
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);

  return (
    <>
      {values.selectedHousehold || values.selectedIndividual ? (
        <LookUpHouseholdIndividualDisplay
          setLookUpDialogOpen={setLookUpDialogOpen}
          values={values}
          onValueChange={onValueChange}
        />
      ) : (
        <LookUp onClick={() => setLookUpDialogOpen(true)}>
          <MarginRightSpan>
            <SearchIcon />
          </MarginRightSpan>
          <span>Look up Household / Individual</span>
        </LookUp>
      )}
      <LookUpHouseholdIndividualModal
        lookUpDialogOpen={lookUpDialogOpen}
        setLookUpDialogOpen={setLookUpDialogOpen}
        initialValues={values}
        onValueChange={onValueChange}
      />
    </>
  );
};
