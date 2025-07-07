import { get, writable } from 'svelte/store';
import { scenariosCreateBody } from '$lib/api/scenarios/scenarios.zod';
import { z } from 'zod';
import { zod } from 'sveltekit-superforms/adapters';
import { defaults, superForm, type SuperForm } from 'sveltekit-superforms';
import { createScenariosCreate } from '$lib/api/scenarios/scenarios';
import { goto } from '$app/navigation';

type ScenarioFormData = z.infer<typeof scenariosCreateBody>;

const mutation = createScenariosCreate({
  mutation: {
    onSuccess: () => {
      // Go to scenario page
      goto('/dashboard/scenarios');
    },
    onError: (error) => {
      console.error('Error creating scenario:', error);
      // TODO: Handle error, e.g., show a notification
    }
  }
});

const form = superForm(defaults(zod(scenariosCreateBody)), {
  validators: zod(scenariosCreateBody),
  SPA: true,
  dataType: 'json',
  onUpdate({ form }) {
    if (!form.valid) return;
    get(mutation).mutate({ data: form.data });
  }
});

interface FormState {
  currentStep: number;
  totalSteps: number;
  form: SuperForm<ScenarioFormData>;
  isValid: Record<number, boolean>;
  touched: Record<number, boolean>;
}

const initialState: FormState = {
  currentStep: 0,
  totalSteps: 7,
  form: form,
  isValid: {},
  touched: {}
};

export const formState = writable<FormState>(initialState);

export const formActions = {
  nextStep: () =>
    formState.update((state) => ({
      ...state,
      currentStep: Math.min(state.currentStep + 1, state.totalSteps - 1)
    })),

  prevStep: () =>
    formState.update((state) => ({
      ...state,
      currentStep: Math.max(state.currentStep - 1, 0)
    })),

  goToStep: (step: number) =>
    formState.update((state) => ({
      ...state,
      currentStep: Math.max(0, Math.min(step, state.totalSteps - 1))
    })),

  setStepValid: (step: number, valid: boolean) =>
    formState.update((state) => ({
      ...state,
      isValid: { ...state.isValid, [step]: valid }
    })),

  setStepTouched: (step: number) =>
    formState.update((state) => ({
      ...state,
      touched: { ...state.touched, [step]: true }
    }))
};
