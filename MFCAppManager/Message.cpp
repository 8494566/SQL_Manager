// Message.cpp : 实现文件
//

#include "stdafx.h"
#include "MFCAppManager.h"
#include "Message.h"
#include "afxdialogex.h"


// Message 对话框

IMPLEMENT_DYNAMIC(Message, CDialogEx)

Message::Message(CWnd* pParent /*=NULL*/)
	: CDialogEx(IDD_DIALOG_MESSAGE, pParent)
	, m_name(_T(""))
	, m_level(_T(""))
	, m_point(_T(""))
	, m_money(_T(""))
	, m_expall(_T(""))
	, m_sex(_T(""))
	, m_camp(_T(""))
	, m_user_id(_T(""))
{

}

Message::~Message()
{
}

void Message::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
	DDX_Text(pDX, IDC_EDITNAME_NEW_NAME, m_name);
	DDX_Text(pDX, IDC_STATIC_EXPLEVEL_S, m_level);
	DDX_Text(pDX, IDC_EDITPOINT_S, m_point);
	DDX_Text(pDX, IDC_EDITPOINT_HOLD_S, m_money);
	DDX_Text(pDX, IDC_EDITPOINTEXP_S, m_expall);
	DDX_Text(pDX, IDC_EDITNAME_NEW2_S, m_sex);
	DDX_Text(pDX, IDC_EDITNAME_NEW3_S, m_camp);
	DDX_Text(pDX, IDC_EDITNAME_NEW_ID_S, m_user_id);
}


BEGIN_MESSAGE_MAP(Message, CDialogEx)
	ON_EN_CHANGE(IDC_EDITNAME_NEW_NAME, &Message::OnEnChangeEditnameNewName)
	ON_EN_CHANGE(IDC_STATIC_EXPLEVEL_S, &Message::OnEnChangeStaticExplevelS)
	ON_EN_CHANGE(IDC_EDITPOINT_S, &Message::OnEnChangeEditpointS)
	ON_EN_CHANGE(IDC_EDITPOINT_HOLD_S, &Message::OnEnChangeEditpointHoldS)
	ON_EN_CHANGE(IDC_EDITPOINTEXP_S, &Message::OnEnChangeEditpointexpS)
	ON_EN_CHANGE(IDC_EDITNAME_NEW2_S, &Message::OnEnChangeEditnameNew2S)
	ON_EN_CHANGE(IDC_EDITNAME_NEW3_S, &Message::OnEnChangeEditnameNew3S)
	ON_EN_CHANGE(IDC_EDITNAME_NEW_ID_S, &Message::OnEnChangeEditnameNewIdS)
END_MESSAGE_MAP()


// Message 消息处理程序


void Message::OnEnChangeEditnameNewName()
{
	UpdateData(TRUE);
	UpdateData(FALSE);
}


void Message::OnEnChangeStaticExplevelS()
{
	UpdateData(TRUE);
	UpdateData(FALSE);
}


void Message::OnEnChangeEditpointS()
{
	UpdateData(TRUE);
	UpdateData(FALSE);
}


void Message::OnEnChangeEditpointHoldS()
{
	UpdateData(TRUE);
	UpdateData(FALSE);
}


void Message::OnEnChangeEditpointexpS()
{
	UpdateData(TRUE);
	UpdateData(FALSE);
}


void Message::OnEnChangeEditnameNew2S()
{
	UpdateData(TRUE);
	UpdateData(FALSE);
}


void Message::OnEnChangeEditnameNew3S()
{
	UpdateData(TRUE);
	UpdateData(FALSE);
}


void Message::OnEnChangeEditnameNewIdS()
{
	UpdateData(TRUE);
	UpdateData(FALSE);
}

void Message::UpData(CString name, CString level, CString point, CString money, CString expall, CString sex, CString camp, CString user_id)
{
	m_name = name;
	m_level = level;
	m_point = point;
	m_money = money;
	m_expall = expall;
	m_sex = sex;
	m_camp = camp;
	m_user_id = user_id;
}
