import { NextResponse, type NextRequest } from 'next/server'
import { updateSession } from '../../utils/supabase/middleware'
import { isUserAllowedToAccessStream, isUserAuthenticated } from '@/api'

const protectedRoutes = ['/stream', '/stream/create']
const userSpecificProtectedRoutes = ['/stream/:streamid']

export async function middleware(req: NextRequest) {
  // update user's auth session
  const supabaseResponse = await updateSession(req)
  const path = req.nextUrl.pathname
  const isProtectedRoute = protectedRoutes.includes(path)
  const isUserSpecificProtectedRoute = userSpecificProtectedRoutes.includes(path)
  const parts = path.split('/');
  const streamId = parts[parts.length - 1]; // Get the last element
 
  // Redirect to homepage (root) if the user is not authenticated
  if (isProtectedRoute && !isUserAuthenticated()) {
    return NextResponse.redirect(new URL('/', req.nextUrl))
  }
 
  // If user tries to access a stream that they are not allowed to access, redirect to their stream dashboard
  if (
    isUserSpecificProtectedRoute && !isUserAllowedToAccessStream(streamId)
  ) {
    return NextResponse.redirect(new URL('/stream', req.nextUrl))
  }
 
  return supabaseResponse
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * Feel free to modify this pattern to include more paths.
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}