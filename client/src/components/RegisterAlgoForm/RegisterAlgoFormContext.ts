import { createFormContext } from '@mantine/form';

export interface RegisterAlgoFormValues {
  algorithm_name: string
}

export const [RegisterAlgoFormProvider, useRegisterAlgoFormContext, useRegisterAlgoForm] =
  createFormContext<RegisterAlgoFormValues>();
