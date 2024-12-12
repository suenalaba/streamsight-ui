import React from 'react'

const page = async ({
  params,
}: {
  params: Promise<{ streamid: string }>
}) => {
  const streamId = (await params).streamid
  return <div>My Stream ID: {streamId}</div>
}

export default page;