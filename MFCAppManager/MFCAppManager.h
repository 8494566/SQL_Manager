
// MFCAppManager.h : PROJECT_NAME Ӧ�ó������ͷ�ļ�
//

#pragma once

#ifndef __AFXWIN_H__
	#error "�ڰ������ļ�֮ǰ������stdafx.h�������� PCH �ļ�"
#endif

#include "resource.h"		// ������


// CMFCAppManagerApp: 
// �йش����ʵ�֣������ MFCAppManager.cpp
//

class CMFCAppManagerApp : public CWinApp
{
public:
	CMFCAppManagerApp();

// ��д
public:
	virtual BOOL InitInstance();

// ʵ��

	DECLARE_MESSAGE_MAP()
};

extern CMFCAppManagerApp theApp;