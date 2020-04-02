import React from 'react';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../shared/Formik/FormikTextField';

export function SubField({ field, form, subField, ...otherProps }) {
  //eslint-disable-next-line
  // debugger
  switch (subField.type) {
    case 'SELECT_ONE':
      return (
        <FormikSelectField
          field={field}
          form={form}
          label={subField.labelEn}
          choices={subField.choices}
          value={field.value[0] || null}
          {...otherProps}
        />
      );
    case 'INTEGER':
      return (
        <>
          <FormikTextField
            field={field}
            form={form}
            decoratorStart={null}
            decoratorEnd={null}
            precision={0}
            label={subField.labelEn}
            type='number'
            value={field.value}
            {...otherProps}
          />
          {/* <FormikTextField
            field={field}
            form={form}
            decoratorStart={null}
            decoratorEnd={null}
            precision={0}
            label={subField.labelEn}
            type='number'
            {...otherProps}
          /> */}
        </>
      );
    default:
      return <div>Other fields</div>;
  }
}
