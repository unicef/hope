import React from 'react';
import { FormikSelectField } from '../../shared/Formik/FormikSelectField';
import { FormikTextField } from '../../shared/Formik/FormikTextField';
import { Field } from 'formik';


export function SubField({ subField }) {
  //props {field, form, subField, ...otherProps}
  //eslint-disable-next-line
  debugger
  return (<p>dupa</p>)
  // switch (subField.type) {
  //   case 'SELECT_ONE':
  //     return (
  //       <FormikSelectField
  //         field={field}
  //         form={form}
  //         label={subField.labelEn}
  //         choices={subField.choices}
  //         value={field.value[0] || null}
  //         {...otherProps}
  //       />
  //     );
  //   case 'INTEGER':
  //     return (
  //       <>
  //     <Field
  //       field={field}
  //       name={`${field.name}.from`}
  //       form={form}
  //       decoratorStart={null}
  //       decoratorEnd={null}
  //       precision={null}
  //       label={`${subField.labelEn} from`}
  //       type='number'
  //       {...otherProps}
  //     />
  //     <FormikTextField
  //       field={field}
  //       name={`${field.name}.to`}
  //       form={form}
  //       decoratorStart={null}
  //       decoratorEnd={null}
  //       precision={null}
  //       label={`${subField.labelEn} to`}
  //       type='number'
  //       {...otherProps}
  //     />
  //     </>
  //     );
  //   default:
  //     return <div>Other fields</div>;
  // }
}
