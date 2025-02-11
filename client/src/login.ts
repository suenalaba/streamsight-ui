import { redirect } from 'next/navigation'
import { createClient } from '../utils/supabase/client'
import { BASE_CLIENT_URL } from './constants'

export async function login() {
  const supabase = createClient()

  await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: `${BASE_CLIENT_URL}/auth/callback`,
    },
  })
}

export async function logout() {
  const supabase = createClient()

  await supabase.auth.signOut()
  redirect('/')
}
