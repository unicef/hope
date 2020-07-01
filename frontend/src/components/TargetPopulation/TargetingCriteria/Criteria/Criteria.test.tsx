import React from 'react';
import { render, wait } from '@testing-library/react';
import { CriteriaField } from './Criteria';

const EqualsCriteria = {
  arguments: ["OTHER"],
  comparisionMethod: "EQUALS",
  isFlexField: false,
  fieldName: 'residence_status',
  fieldAttribute: {
    labelEn: 'Residence Status',
    name: 'residence_status',
    type: 'SELECT_ONE',
    choices: [{
      value: 'OTHER',
      labelEn: "Other",
    }]
  }
}

const RangeCriteria = {
  arguments: [20,54],
  comparisionMethod: "RANGE",
  isFlexField: false,
  fieldName: 'age',
  fieldAttribute: {
    labelEn: 'Residence Status',
    name: 'residence_status',
    type: 'INTEGER',
    choices: []
  }
}

const NotEqualsCriteria = {
  arguments: [20],
  comparisionMethod: "NOT_EQUALS",
  isFlexField: false,
  fieldName: 'age',
  fieldAttribute: {
    labelEn: 'Not equals',
    name: 'residence_status',
    type: 'INTEGER',
    choices: []
  }
}

const LessThanCriteria = {
  arguments: [20],
  comparisionMethod: "LESS_THEN",
  isFlexField: false,
  fieldName: 'age',
  fieldAttribute: {
    labelEn: 'Less Then',
    name: 'residence_status',
    type: 'INTEGER',
    choices: []
  }
}

const GreaterThanCriteria = {
  arguments: [20],
  comparisionMethod: "GREATER_THAN",
  isFlexField: false,
  fieldName: 'age',
  fieldAttribute: {
    labelEn: 'Greater Than',
    name: 'residence_status',
    type: 'INTEGER',
    choices: []
  }
}

const ContainsCriteria = {
  arguments: [20],
  comparisionMethod: "CONTAINS",
  isFlexField: false,
  fieldName: 'age',
  fieldAttribute: {
    labelEn: 'Contains',
    name: 'residence_status',
    type: 'INTEGER',
    choices: []
  }
}


describe('Criteria', () => {
  test('Return criteria element for NOT_EQUALS', () => {
    const { container } = render(
      <CriteriaField field={NotEqualsCriteria}/>
    )
    wait(() => expect(container).toContainElement(container.querySelector('.not-equals')))
  })
  test('Returns criteria element for EQUALS', () => {
    const { container } = render(
      <CriteriaField field={EqualsCriteria}/>
    )
    wait(() => expect(container).toContainElement(container.querySelector('.equals')))
  })
  test('Return criteria element for RANGE', () => {
    const { container } = render(
      <CriteriaField field={RangeCriteria}/>
    )
    wait(() => expect(container).toContainElement(container.querySelector('.range')))
  })
  test('Return criteria element for LESS_THAN', () => {
    const { container } = render(
      <CriteriaField field={LessThanCriteria}/>
    )
    wait(() => expect(container).toContainElement(container.querySelector('.less-than')))
  })
  test('Return criteria element for CONTAINS', () => {
    const { container } = render(
      <CriteriaField field={ContainsCriteria}/>
    )
    wait(() => expect(container).toContainElement(container.querySelector('.contains')))
  })
})